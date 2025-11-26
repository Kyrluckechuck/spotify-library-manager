"""Download tasks for the Spotify library manager."""

import time
from typing import Any, Optional

from django.db.models.functions import Now

from celery_app import app as celery_app
from downloader.utils import sanitize_and_strip_url
from lib.config_class import Config

from ..models import (
    ALBUM_GROUPS_TO_IGNORE,
    ALBUM_TYPES_TO_DOWNLOAD,
    Album,
    Artist,
    TaskHistory,
)
from .core import (
    TaskCancelledException,
    check_and_update_progress,
    check_if_cancelled,
    check_task_cancellation,
    complete_task,
    create_task_history,
    logger,
    require_download_capability,
    spotdl_wrapper,
    update_task_progress,
)


@celery_app.task(
    bind=True, name="library_manager.tasks.download_missing_albums_for_artist"
)
def download_missing_albums_for_artist(
    self: Any, artist_id: int, delay: int = 0
) -> None:
    # pylint: disable=too-many-return-statements
    task_history = None
    try:
        # Add delay (if applicable) to reduce chance of flagging when backfilling library
        time.sleep(delay)

        # Check if artist exists before proceeding
        try:
            artist = Artist.objects.get(id=artist_id)
        except Artist.DoesNotExist:
            logger.warning(f"Artist with ID {artist_id} does not exist. Skipping task.")
            return

        # Create task history record
        task_history = create_task_history(
            task_id=self.request.id,
            task_type="DOWNLOAD",
            entity_id=artist.gid,
            entity_type="ARTIST",
        )
        update_task_progress(
            task_history, 0.0, f"Starting download for artist {artist.name}"
        )

        # Check authentication before proceeding
        require_download_capability(task_history)

        # Check for cancellation before proceeding
        if check_task_cancellation(task_history):
            logger.info(f"Task cancelled for artist {artist.name}")
            return

        missing_albums = Album.objects.filter(
            artist=artist,
            downloaded=False,
            wanted=True,
            album_type__in=ALBUM_TYPES_TO_DOWNLOAD,
        ).exclude(album_group__in=ALBUM_GROUPS_TO_IGNORE)
        logger.info(
            f"missing albums search for artist {artist.gid} found {missing_albums.count()}"
        )

        # Check for cancellation and update progress
        if check_and_update_progress(
            task_history, 25.0, f"Found {missing_albums.count()} missing albums"
        ):
            logger.info(f"Task cancelled during album search for artist {artist.name}")
            return

        downloader_config = Config()

        # Check for cancellation before preparing config
        if check_and_update_progress(
            task_history, 50.0, "Preparing download configuration"
        ):
            logger.info(
                f"Task cancelled during config preparation for artist {artist.name}"
            )
            return

        downloader_config.urls = (
            []
        )  # This must be reset or it will persist between runs
        if missing_albums.count() > 0:
            for missing_album in missing_albums:
                downloader_config.urls.append(missing_album.spotify_uri)

            logger.info(
                f"missing albums search for artist {artist.gid} kicking off {len(downloader_config.urls)}"
            )

            # Check for cancellation before download
            if check_and_update_progress(
                task_history,
                75.0,
                f"Downloading {len(downloader_config.urls)} albums",
            ):
                logger.info(f"Task cancelled before download for artist {artist.name}")
                return

            # Create callback to update task progress during long downloads
            def progress_callback(progress_pct: float, message: str) -> None:
                # Check for cancellation during download (checks both TaskResult and TaskHistory)
                try:
                    check_if_cancelled(self.request.id)
                except TaskCancelledException:
                    logger.info(f"Download cancelled by user for artist {artist.name}")
                    raise
                update_task_progress(task_history, progress_pct, message)

            try:
                spotdl_wrapper.execute(
                    downloader_config, task_progress_callback=progress_callback
                )
            except TaskCancelledException as e:
                logger.info(f"Task cancelled during download: {e}")
                if task_history:
                    task_history.status = "CANCELLED"
                    task_history.error_message = "Cancelled by user"
                    task_history.save()
                return
        else:
            logger.info(
                f"missing albums search for artist {artist.gid} is skipping since there are none missing"
            )
            if task_history:
                update_task_progress(
                    task_history, 100.0, "No missing albums to download"
                )

        # Final cancellation check before marking complete
        if check_task_cancellation(task_history):
            logger.info(f"Task cancelled before completion for artist {artist.name}")
            return

        # Update last_downloaded_at timestamp (download completed)
        artist.last_downloaded_at = Now()
        artist.save()

        if task_history:
            complete_task(task_history, success=True)

    except Exception as e:
        logger.error("Error in sync_tracked_playlist_internal: %s", e, exc_info=True)
        if task_history:
            complete_task(task_history, success=False, error_message=str(e))
        raise


@celery_app.task(bind=True, name="library_manager.tasks.download_single_album")
def download_single_album(self: Any, album_id: int) -> None:
    """Download a single specific album by ID."""
    task_history = None
    try:
        # Check if album exists before proceeding
        try:
            album = Album.objects.get(id=album_id)
        except Album.DoesNotExist:
            logger.warning(f"Album with ID {album_id} does not exist. Skipping task.")
            return

        # Create task history record for the album
        task_history = create_task_history(
            task_id=self.request.id,
            task_type="DOWNLOAD",
            entity_id=album.spotify_gid,
            entity_type="ALBUM",
        )
        update_task_progress(
            task_history, 0.0, f"Starting download for album {album.name}"
        )

        # Check authentication before proceeding
        require_download_capability(task_history)

        # Check for cancellation before proceeding
        if check_task_cancellation(task_history):
            logger.info(f"Task cancelled for album {album.name}")
            return

        # Ensure album is marked as wanted
        if not album.wanted:
            album.wanted = True
            album.save()

        if check_and_update_progress(
            task_history, 25.0, "Preparing download configuration"
        ):
            logger.info(
                f"Task cancelled during config preparation for album {album.name}"
            )
            return

        downloader_config = Config()
        downloader_config.urls = [album.spotify_uri]

        if check_and_update_progress(
            task_history, 50.0, f"Downloading album {album.name}"
        ):
            logger.info(f"Task cancelled before download for album {album.name}")
            return

        # Perform the download
        logger.info(
            f"Downloading album: {album.name} (spotify_uri: {album.spotify_uri})"
        )
        spotdl_wrapper.execute(downloader_config)

        # Mark album as downloaded
        album.downloaded = True
        album.save()

        if check_and_update_progress(task_history, 100.0, "Download completed"):
            logger.info(f"Task cancelled after download for album {album.name}")
            return

        complete_task(task_history, success=True)
        logger.info(f"Successfully downloaded album: {album.name}")

    except Exception as e:
        error_msg = f"Error downloading album: {str(e)}"
        logger.error(error_msg)
        if task_history:
            complete_task(task_history, success=False, error_message=error_msg)
        raise


@celery_app.task(bind=True, name="library_manager.tasks.download_playlist")
def download_playlist(
    self: Any,
    playlist_url: str,
    tracked: bool = True,
    force_playlist_resync: bool = False,
    task_id: Optional[str] = None,
) -> None:
    task_history = None
    try:
        # Use the Celery task ID if no task_id is provided
        if task_id is None:
            task_id = self.request.id

        playlist_url = sanitize_and_strip_url(playlist_url)

        # Extract playlist ID from URL for task history
        playlist_id = (
            playlist_url.split(":")[-1] if ":" in playlist_url else playlist_url
        )

        # Create task history record (always create, even without Celery context)
        task_history = create_task_history(
            task_id=task_id,
            task_type="DOWNLOAD",
            entity_id=playlist_id,
            entity_type="PLAYLIST",
            task_name="download_playlist",
        )

        # Check authentication before proceeding
        require_download_capability(task_history)

        update_task_progress(
            task_history, 0.0, f"Starting playlist download: {playlist_url}"
        )
        # Mark as running
        task_history.status = "RUNNING"
        task_history.save()

        # Check for cancellation before proceeding
        if check_task_cancellation(task_history):
            logger.info(f"Playlist download cancelled: {playlist_url}")
            return

        downloader_config = Config(
            urls=[playlist_url],
            track_artists=tracked,
            force_playlist_resync=force_playlist_resync,
        )

        # Check for cancellation before download
        if check_and_update_progress(task_history, 50.0, "Downloading playlist tracks"):
            logger.info(f"Playlist download cancelled before download: {playlist_url}")
            return

        # Create callback to update task progress during playlist download
        def playlist_progress_callback(progress_pct: float, message: str) -> None:
            # Check for cancellation during download (checks both TaskResult and TaskHistory)
            try:
                check_if_cancelled(task_id)
            except TaskCancelledException:
                logger.info(f"Playlist download cancelled by user: {playlist_url}")
                raise
            update_task_progress(
                task_history, 50.0 + (progress_pct / 2), message
            )  # Scale to 50-100%

        try:
            spotdl_wrapper.execute(
                downloader_config, task_progress_callback=playlist_progress_callback
            )
        except TaskCancelledException as e:
            logger.info(f"Playlist download cancelled: {e}")
            if task_history:
                task_history.status = "CANCELLED"
                task_history.error_message = "Cancelled by user"
                task_history.save()
            return

        # Final cancellation check
        if check_task_cancellation(task_history):
            logger.info(
                f"Playlist download cancelled before completion: {playlist_url}"
            )
            return

        complete_task(task_history, success=True)

    except Exception as e:
        if task_history:
            complete_task(task_history, success=False, error_message=str(e))
        raise


@celery_app.task(
    bind=True, name="library_manager.tasks.download_extra_album_types_for_artist"
)
def download_extra_album_types_for_artist(
    self: Any, artist_id: int, task_id: Optional[str] = None
) -> None:
    # Check authentication before proceeding with any DB queries
    require_download_capability()

    # Check if artist exists before proceeding
    try:
        artist = Artist.objects.get(id=artist_id)
    except Artist.DoesNotExist:
        logger.warning(f"Artist with ID {artist_id} does not exist. Skipping task.")
        return

    missing_albums = Album.objects.filter(
        artist=artist,
        downloaded=False,
        wanted=True,
        album_group__in=ALBUM_GROUPS_TO_IGNORE,
    )
    logger.info(
        f"extra album missing albums search for artist {artist.gid} found {missing_albums.count()}"
    )
    downloader_config = Config()
    downloader_config.urls = []  # This must be reset or it will persist between runs
    if missing_albums.count() > 0:
        for missing_album in missing_albums:
            downloader_config.urls.append(missing_album.spotify_uri)

        logger.info(
            f"extra album missing albums search for artist {artist.gid} kicking off {len(downloader_config.urls)}"
        )

        # Create progress callback if task history is available
        task_progress_callback = None
        if task_id:
            task_history = TaskHistory.objects.filter(task_id=task_id).first()
            if task_history:
                # Capture task_history in closure to avoid cell-var-from-loop
                captured_task_history = task_history

                def update_task_progress_callback(
                    progress_pct: float, message: str
                ) -> None:
                    captured_task_history.update_progress(progress_pct)

                task_progress_callback = update_task_progress_callback

        spotdl_wrapper.execute(downloader_config, task_progress_callback)
    else:
        logger.info(
            f"extra album missing albums search for artist {artist.gid} is skipping since there are none missing"
        )
    # Update last_downloaded_at timestamp (extra albums download completed)
    artist.last_downloaded_at = Now()
    artist.save()


@celery_app.task(bind=True, name="library_manager.tasks.download_album_by_spotify_id")
def download_album_by_spotify_id(self: Any, spotify_album_id: str) -> None:
    """
    Download an album by its Spotify ID (not database ID).

    This task fetches album metadata from Spotify if needed, creates/gets the album
    in the database, and then queues the actual download.
    """
    task_history = None
    try:
        from downloader.downloader import Downloader

        from library_manager.validators import (
            extract_spotify_id_from_uri,
            normalize_spotify_gid,
        )

        # Create task history record
        task_history = create_task_history(
            task_id=self.request.id,
            task_type="DOWNLOAD",
            entity_id=spotify_album_id,
            entity_type="ALBUM",
        )
        update_task_progress(
            task_history, 0.0, f"Starting download for album {spotify_album_id}"
        )

        # Check authentication before proceeding
        require_download_capability(task_history)

        # Check for cancellation before proceeding
        if check_task_cancellation(task_history):
            logger.info(f"Task cancelled for album {spotify_album_id}")
            return

        # Check if album already exists in DB
        try:
            album = Album.objects.get(spotify_gid=spotify_album_id)
            logger.info(f"Album {album.name} already exists in database")
        except Album.DoesNotExist:
            # Fetch from Spotify
            update_task_progress(
                task_history, 25.0, "Fetching album metadata from Spotify"
            )

            # Get SpotifyClient from spotdl_wrapper
            spotify_client = spotdl_wrapper.spotipy_client
            downloader = Downloader(spotify_client)

            album_data = downloader.get_album(spotify_album_id)
            if not album_data:
                raise ValueError(
                    f"Album {spotify_album_id} not found on Spotify"
                ) from None

            # Get or create the artist
            artist_data = album_data.get("artists", [{}])[0]
            if not artist_data:
                raise ValueError(
                    f"Album {spotify_album_id} has no artist data"
                ) from None

            raw_artist_id = artist_data.get("id") or artist_data.get("uri")
            if not raw_artist_id:
                raise ValueError(
                    "Album artist missing both 'id' and 'uri' fields"
                ) from None

            artist_gid = extract_spotify_id_from_uri(raw_artist_id)
            if not artist_gid:
                raise ValueError(f"Invalid artist ID/URI: {raw_artist_id}") from None

            artist_gid = normalize_spotify_gid(artist_gid)

            artist, _ = Artist.objects.get_or_create(
                gid=artist_gid,
                defaults={"name": artist_data.get("name", "Unknown Artist")},
            )

            # Create the album
            album = Album.objects.create(
                spotify_gid=album_data["id"],
                artist=artist,
                spotify_uri=album_data.get("uri", f"spotify:album:{album_data['id']}"),
                total_tracks=album_data.get("total_tracks", 0),
                name=album_data.get("name", "Unknown Album"),
                album_type=album_data.get("album_type"),
                wanted=True,
            )
            logger.info(f"Created album: {album.name}")

        # Mark album as wanted if not already
        if not album.wanted:
            album.wanted = True
            album.save()

        update_task_progress(task_history, 50.0, f"Downloading album: {album.name}")

        # Now download using the standard single album task logic inline
        # (avoiding task chaining complexity)
        downloader_config = Config()
        downloader_config.urls = [album.spotify_uri]

        spotdl_wrapper.execute(downloader_config)

        # Mark album as downloaded
        album.downloaded = True
        album.save()

        complete_task(task_history, success=True)
        logger.info(f"Successfully downloaded album: {album.name}")

    except Exception as e:
        error_msg = f"Error downloading album: {str(e)}"
        logger.error(error_msg)
        if task_history:
            complete_task(task_history, success=False, error_message=error_msg)
        raise


@celery_app.task(bind=True, name="library_manager.tasks.download_single_track")
def download_single_track(self: Any, track_id: str) -> None:
    """
    Download a single track by its Spotify ID.

    Downloads only the requested track, not the entire album.
    """
    task_history = None
    try:
        # Create task history record
        task_history = create_task_history(
            task_id=self.request.id,
            task_type="DOWNLOAD",
            entity_id=track_id,
            entity_type="TRACK",
        )
        update_task_progress(
            task_history, 0.0, f"Starting download for track {track_id}"
        )

        # Check authentication before proceeding
        require_download_capability(task_history)

        # Check for cancellation before proceeding
        if check_task_cancellation(task_history):
            logger.info(f"Task cancelled for track {track_id}")
            return

        # Build the track URI
        track_uri = f"spotify:track:{track_id}"

        update_task_progress(task_history, 25.0, f"Downloading track: {track_id}")

        # Download just this single track using spotdl
        downloader_config = Config()
        downloader_config.urls = [track_uri]

        # Execute download with progress callback
        def task_progress_callback(progress_pct: float, message: str = "") -> None:
            # Scale progress: 25% (start) to 95% (before completion)
            scaled_progress = 25.0 + (progress_pct * 0.70)
            update_task_progress(task_history, scaled_progress, message)

        spotdl_wrapper.execute(downloader_config, task_progress_callback)

        complete_task(task_history, success=True)
        logger.info(f"Successfully downloaded track: {track_id}")

    except Exception as e:
        error_msg = f"Error downloading track: {str(e)}"
        logger.error(error_msg)
        if task_history:
            complete_task(task_history, success=False, error_message=error_msg)
        raise
