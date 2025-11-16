import time
import uuid
from typing import Optional, cast

from django.conf import settings
from django.db.models.functions import Now
from django.utils import timezone

from celery.utils.log import get_task_logger
from celery_app import app as celery_app
from downloader.spotdl_wrapper import SpotdlWrapper
from downloader.spotipy_tasks import track_artists_in_playlist
from downloader.utils import sanitize_and_strip_url
from lib.config_class import Config

from . import helpers
from .models import (
    ALBUM_GROUPS_TO_IGNORE,
    ALBUM_TYPES_TO_DOWNLOAD,
    Album,
    Artist,
    DownloadHistory,
    Song,
    TaskHistory,
    TrackedPlaylist,
)

# Initialize SpotdlWrapper
spotdl_wrapper = SpotdlWrapper(Config())

# Initialize Celery logger
logger = get_task_logger(__name__)


def create_task_history(
    task_id: Optional[str] = None,
    task_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    task_name: Optional[str] = None,
) -> TaskHistory:
    """Create a task history record for tracking task execution"""
    if task_id is None:
        # Create task ID if not provided
        entity_type_str = entity_type or "unknown"
        if entity_id:
            generated_task_id = f"{task_type}-{entity_type_str.lower()}-{entity_id}"
        else:
            generated_task_id = f"{task_name or 'unknown'}-{uuid.uuid4().hex[:8]}"
    else:
        generated_task_id = task_id

    # Check if task history already exists for this task
    existing_task = TaskHistory.objects.filter(task_id=generated_task_id).first()
    if existing_task:
        return existing_task

    # Create new task history record
    task_history = TaskHistory(
        task_id=generated_task_id,
        type=task_type or "UNKNOWN",
        entity_id=str(entity_id) if entity_id else "unknown",
        entity_type=entity_type or "UNKNOWN",
        status="PENDING",
    )
    task_history.save()
    return task_history


def update_task_progress(
    task_history: TaskHistory, progress: float, message: Optional[str] = None
) -> None:
    """Update task progress, heartbeat, and add log message"""
    task_history.status = "RUNNING"
    task_history.progress_percentage = progress
    task_history.update_heartbeat()  # Update heartbeat on progress
    if message:
        task_history.add_log_message(message)
    task_history.save()


def update_task_heartbeat(task_history: TaskHistory) -> None:
    """Update task heartbeat (no log message)"""
    task_history.update_heartbeat()


def complete_task(
    task_history: TaskHistory, success: bool = True, error_message: Optional[str] = None
) -> None:
    """Mark task as completed or failed"""
    if success:
        task_history.mark_completed()
    else:
        task_history.mark_failed(error_message)


def check_task_cancellation(task_history: TaskHistory) -> bool:
    """Check if the task has been cancelled by checking the database status."""
    # Refresh from database to get latest status
    task_history.refresh_from_db()
    status_str: str = cast(str, task_history.status)
    return status_str == "CANCELLED"


def check_and_update_progress(
    task_history: TaskHistory, progress: float, message: Optional[str] = None
) -> bool:
    """Update task progress and check for cancellation. Returns True if cancelled."""
    if check_task_cancellation(task_history):
        return True

    update_task_progress(task_history, progress, message)
    return False


def require_download_capability(task_history: Optional[TaskHistory] = None) -> None:
    """Check authentication status and block task execution if downloads are not possible.

    This function verifies that the system has valid authentication (cookies) before
    allowing download tasks to proceed. If authentication is invalid or expired, the
    task is failed immediately to prevent wasted API calls.

    Args:
        task_history: Optional task history to update with failure status if auth fails

    Raises:
        RuntimeError: If downloads are not possible due to authentication issues
    """
    from src.services.system_health import SystemHealthService

    can_download, reason = SystemHealthService.is_download_capable()
    if not can_download:
        error_msg = f"Cannot download: {reason}"
        logger.error(error_msg)
        if task_history:
            task_history.status = "FAILED"
            task_history.add_log_message(error_msg)
            task_history.save()
        raise RuntimeError(error_msg)


def fetch_all_albums_for_artist_sync(artist_id: int) -> None:
    """Synchronous wrapper for fetch_all_albums_for_artist - for direct calls."""
    fetch_all_albums_for_artist.delay(artist_id)


@celery_app.task(
    bind=True, priority=3, name="library_manager.tasks.fetch_all_albums_for_artist"
)
def fetch_all_albums_for_artist(self, artist_id: int) -> None:
    task_history = None
    try:
        # Check if artist exists before proceeding
        try:
            artist = Artist.objects.get(id=artist_id)
        except Artist.DoesNotExist:
            logger.warning(f"Artist with ID {artist_id} does not exist. Skipping task.")
            return

        # Create task history record (always create, even without Celery context)
        task_history = create_task_history(
            task_id=self.request.id,
            task_type="FETCH",
            entity_id=artist.gid,
            entity_type="ARTIST",
            task_name="fetch_all_albums_for_artist",
        )
        update_task_progress(
            task_history, 0.0, f"Starting fetch for artist {artist.name}"
        )
        # Mark as running
        task_history.status = "RUNNING"
        task_history.save()

        # Check authentication before proceeding
        require_download_capability(task_history)

        # Check for cancellation before proceeding
        if check_task_cancellation(task_history):
            logger.info(f"Task cancelled for artist {artist.name}")
            return

        downloader_config = Config()
        downloader_config.artist_to_fetch = artist.gid
        downloader_config.urls = []

        # TODO: Re-enable ProcessInfo after fixing circular imports
        # if self is not None:
        #     from src.services.monitor import ProcessInfo
        #     process_info = ProcessInfo(
        #         self, desc=f"fetch all albums for artist (artist.gid: {artist.gid})"
        #     )
        #     downloader_config.process_info = process_info

        # Check for cancellation before major operation
        if check_and_update_progress(
            task_history, 25.0, "Fetching artist albums from Spotify"
        ):
            logger.info(f"Task cancelled during Spotify fetch for artist {artist.name}")
            return

        # Create callback to update task progress during fetch (if task_history exists)
        if task_history:

            def fetch_progress_callback(progress_pct: float, message: str):
                update_task_progress(task_history, progress_pct, message)

            spotdl_wrapper.execute(
                downloader_config, task_progress_callback=fetch_progress_callback
            )
        else:
            spotdl_wrapper.execute(downloader_config)

        # Final cancellation check before completion
        if check_task_cancellation(task_history):
            logger.info(f"Task cancelled before completion for artist {artist.name}")
            return

        complete_task(task_history, success=True)

    except Exception as e:
        if task_history:
            complete_task(task_history, success=False, error_message=str(e))
        raise


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 30},
    name="library_manager.tasks.download_missing_albums_for_artist",
)
def download_missing_albums_for_artist(self, artist_id: int, delay: int = 0) -> None:
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
        # TODO: Re-enable ProcessInfo after fixing circular imports
        # if self is not None and task_history:
        #     process_info = ProcessInfo(
        #         self,
        #         desc=f"artist missing album download (artist.gid: {artist.gid})",
        #         total=1000,
        #     )
        #     downloader_config.process_info = process_info

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
            def progress_callback(progress_pct: float, message: str):
                # Check for cancellation during download
                if check_task_cancellation(task_history):
                    raise InterruptedError(
                        f"Download cancelled by user for artist {artist.name}"
                    )
                update_task_progress(task_history, progress_pct, message)

            try:
                spotdl_wrapper.execute(
                    downloader_config, task_progress_callback=progress_callback
                )
            except InterruptedError as e:
                logger.error(str(e))
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

        artist.last_synced_at = Now()
        artist.save()

        if task_history:
            complete_task(task_history, success=True)

    except Exception as e:
        logger.error("Error in sync_tracked_playlist_internal: %s", e, exc_info=True)
        if task_history:
            complete_task(task_history, success=False, error_message=str(e))
        raise


def _sync_tracked_playlist_internal(
    tracked_playlist: TrackedPlaylist, task_id: Optional[str] = None
) -> None:
    """Internal function that does the actual sync work"""
    task_history = None
    try:
        # Create task history record for the sync operation
        task_history = create_task_history(
            task_id=task_id,
            task_type="SYNC",
            entity_id=str(tracked_playlist.pk),
            entity_type="PLAYLIST",
            task_name="sync_tracked_playlist",
        )
        update_task_progress(
            task_history, 0.0, f"Starting playlist sync: {tracked_playlist.name}"
        )
        # Mark as running
        task_history.status = "RUNNING"
        task_history.save()

        # Enqueue the actual download task
        priority = 2  # Default priority since task.priority not available in Celery
        helpers.enqueue_playlists([tracked_playlist], priority=priority)

        # Mark as completed since the sync operation is done (download is queued separately)
        complete_task(task_history, success=True)

    except Exception as e:
        if task_history:
            complete_task(task_history, success=False, error_message=str(e))
        raise


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 30},
    name="library_manager.tasks.download_single_album",
)
def download_single_album(self, album_id: int) -> None:
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


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 30},
    name="library_manager.tasks.sync_tracked_playlist",
)
def sync_tracked_playlist(
    self, playlist_id: int, task_id: Optional[str] = None
) -> None:
    """Celery task wrapper for sync_tracked_playlist"""
    # Use the Celery task ID if no task_id is provided
    if task_id is None:
        task_id = self.request.id

    # Get the playlist object from the ID
    try:
        tracked_playlist = TrackedPlaylist.objects.get(id=playlist_id)
    except TrackedPlaylist.DoesNotExist:
        logger.warning(
            f"TrackedPlaylist with ID {playlist_id} does not exist. Skipping task."
        )
        return

    _sync_tracked_playlist_internal(tracked_playlist, task_id)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 30},
    name="library_manager.tasks.download_playlist",
)
def download_playlist(
    self,
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

        # TODO: Re-enable ProcessInfo after fixing circular imports
        # if self is not None:
        #     process_info = ProcessInfo(self, desc="playlist download", total=1000)
        #     downloader_config.process_info = process_info

        # Check for cancellation before download
        if check_and_update_progress(task_history, 50.0, "Downloading playlist tracks"):
            logger.info(f"Playlist download cancelled before download: {playlist_url}")
            return

        # Create callback to update task progress during playlist download
        def playlist_progress_callback(progress_pct: float, message: str):
            # Check for cancellation during download
            if check_task_cancellation(task_history):
                raise InterruptedError(
                    f"Playlist download cancelled by user: {playlist_url}"
                )
            update_task_progress(
                task_history, 50.0 + (progress_pct / 2), message
            )  # Scale to 50-100%

        try:
            spotdl_wrapper.execute(
                downloader_config, task_progress_callback=playlist_progress_callback
            )
        except InterruptedError as e:
            logger.error(str(e))
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
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 30},
    name="library_manager.tasks.retry_all_missing_known_songs",
)
def retry_all_missing_known_songs(self, task_id: Optional[str] = None) -> None:
    # Check authentication before proceeding with any DB queries
    require_download_capability()

    missing_known_songs_list = (
        Song.objects.filter(bitrate=0, unavailable=False)
        .order_by("created_at")
        .select_related("primary_artist")
        .filter(primary_artist__tracked=True)[:100]
    )
    failed_known_songs_list = Song.objects.filter(
        failed_count__gt=0, bitrate=0, unavailable=False
    ).order_by("created_at")[:100]
    # Combine results for iterating
    missing_known_songs_list = missing_known_songs_list | failed_known_songs_list

    if missing_known_songs_list.count() == 0:
        logger.info("All songs downloaded, exiting missing known song loop!")
        return

    failed_song_array = [song.spotify_uri for song in missing_known_songs_list]

    logger.info(f"Downloading {len(failed_song_array)} missing songs")
    downloader_config = Config(urls=failed_song_array, track_artists=False)

    # TODO: Re-enable ProcessInfo after fixing circular imports
    # if self is not None:
    #     process_info = ProcessInfo(
    #         self, desc="missing/failed song download", total=1000
    #     )
    #     downloader_config.process_info = process_info

    # Create progress callback if task history is available
    task_progress_callback = None
    if hasattr(self, "request") and self.request.id:
        task_history = TaskHistory.objects.filter(task_id=self.request.id).first()
        if task_history:

            def update_task_progress_callback(progress_pct, message):
                task_history.update_progress(progress_pct, message)

            task_progress_callback = update_task_progress_callback

    spotdl_wrapper.execute(downloader_config, task_progress_callback)

    # Queue up next batch after ensuring rate limit has passed
    retry_all_missing_known_songs.schedule(delay=30)


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 30},
    name="library_manager.tasks.download_extra_album_types_for_artist",
)
def download_extra_album_types_for_artist(
    self, artist_id: int, task_id: Optional[str] = None
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
    # TODO: Re-enable ProcessInfo after fixing circular imports
    # if self is not None:
    #     process_info = ProcessInfo(
    #         self,
    #         desc=f"extra album artist missing album download (artist.gid: {artist.gid})",
    #         total=1000,
    #     )
    #     downloader_config.process_info = process_info
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

                def update_task_progress_callback(progress_pct, message):
                    task_history.update_progress(progress_pct, message)

                task_progress_callback = update_task_progress_callback

        spotdl_wrapper.execute(downloader_config, task_progress_callback)
    else:
        logger.info(
            f"extra album missing albums search for artist {artist.gid} is skipping since there are none missing"
        )
    artist.last_synced_at = Now()
    artist.save()


@celery_app.task(bind=True, name="library_manager.tasks.sync_tracked_playlist_artists")
def sync_tracked_playlist_artists(
    self, playlist_id: int, task_id: Optional[str] = None
) -> None:
    # Given a playlist, track the artists without actually downloading the playlist (potentially, again)
    try:
        playlist = TrackedPlaylist.objects.get(id=playlist_id)
    except TrackedPlaylist.DoesNotExist:
        logger.warning(
            f"TrackedPlaylist with ID {playlist_id} does not exist. Skipping task."
        )
        return

    track_artists_in_playlist(playlist.url, task_id)


@celery_app.task(
    bind=True, name="library_manager.tasks.update_tracked_artists"
)  # Scheduled via Celery Beat
def update_tracked_artists(self, task_id: Optional[str] = None) -> None:
    all_tracked_artists = Artist.objects.filter(tracked=True).order_by(
        "last_synced_at", "added_at", "id"
    )
    helpers.update_tracked_artists_albums(
        [], list(all_tracked_artists), priority=None  # task.priority not available
    )


# Severely throttling automatic playlist download for tracked artists for the time being;
# There is a high likelyhood of being flagged due to high usage at the moment and a new scalable solution needs to be investigated.
@celery_app.task(
    bind=True, name="library_manager.tasks.download_missing_tracked_artists"
)  # Scheduled via Celery Beat
def download_missing_tracked_artists(self, task_id: Optional[str] = None) -> None:
    if settings.disable_missing_tracked_artist_download:
        logger.info(
            "Skipping queued missing tracked artists due to disable_missing_tracked_artist_download setting"
        )
        return

    from datetime import timedelta

    twelve_hours_ago = timezone.now() - timedelta(hours=12)
    recently_downloaded_songs = DownloadHistory.objects.filter(
        added_at__gte=twelve_hours_ago
    )
    if recently_downloaded_songs.count() > 250:
        logger.info(
            f"Skipping queued missing tracked artists due to quantity of recent downloads ({recently_downloaded_songs.count()})"
        )
        return
    # Limit to only desired album types (ignoring `appears_on`), and limit results so this won't throttle
    all_tracked_artists = (
        Artist.objects.filter(
            tracked=True,
            album__downloaded=False,
            album__wanted=True,
            album__album_type__in=ALBUM_TYPES_TO_DOWNLOAD,
        )
        .exclude(album__album_group__in=ALBUM_GROUPS_TO_IGNORE)
        .distinct()
        .order_by("last_synced_at", "added_at", "id")[:150]
    )
    helpers.download_missing_tracked_artists(
        [], list(all_tracked_artists), priority=None
    )


@celery_app.task(
    bind=True, name="library_manager.tasks.sync_tracked_playlists"
)  # Scheduled via Celery Beat
def sync_tracked_playlists(self, task_id: Optional[str] = None) -> None:
    all_enabled_playlists = TrackedPlaylist.objects.filter(enabled=True).order_by(
        "last_synced_at", "id"
    )
    helpers.enqueue_playlists(
        list(all_enabled_playlists), priority=None
    )  # task.priority not available


@celery_app.task(
    bind=True, name="library_manager.tasks.cleanup_stuck_tasks_periodic"
)  # Scheduled via Celery Beat - Every 5 minutes
def cleanup_stuck_tasks_periodic(self) -> None:
    """Periodically clean up stuck tasks and stale artist references"""
    from library_manager.models import TaskHistory

    stuck_count = TaskHistory.cleanup_stuck_tasks()
    if stuck_count > 0:
        logger.info(f"Cleaned up {stuck_count} stuck task(s)")

    # Clean up stale artist references in Celery queue
    # TODO: Implement Celery-based stale task cleanup
    logger.warning("Celery-based stale task cleanup not yet implemented")


@celery_app.task(
    bind=True, name="library_manager.tasks.cleanup_celery_history"
)  # Scheduled via Celery Beat - Daily at 6 AM
def cleanup_celery_history(self, days_to_keep: int = 30) -> None:
    """Periodically clean up old completed/failed task history to prevent database bloat"""
    from library_manager.models import TaskHistory

    deleted_count = TaskHistory.cleanup_old_tasks(days_to_keep=days_to_keep)
    if deleted_count > 0:
        logger.info(f"Cleaned up {deleted_count} old task history record(s)")
    else:
        logger.info("No old task history records to clean up")


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 30},
    name="library_manager.tasks.validate_undownloaded_songs",
)
def validate_undownloaded_songs(
    self,
    task_id: Optional[str] = None,
) -> None:
    # Check authentication before proceeding with any DB queries
    require_download_capability()

    non_downloaded_songs_that_should_exist = Song.objects.filter(
        bitrate__gt=0, unavailable=False, downloaded=False
    ).order_by("created_at")[:500]
    non_downloaded_songs_that_maybe_should_exist = Song.objects.filter(
        bitrate__gt=0, unavailable=True, downloaded=False
    ).order_by("created_at")[:500]

    non_downloaded_songs = (
        non_downloaded_songs_that_should_exist
        | non_downloaded_songs_that_maybe_should_exist
    )

    non_downloaded_songs_count = non_downloaded_songs.count()
    non_downloaded_songs_that_should_exist_count = (
        non_downloaded_songs_that_should_exist.count()
    )

    # No songs to attempt
    if non_downloaded_songs_count == 0:
        logger.info("All songs marked downloaded that should be!")
        return

    missing_song_array = [song.spotify_uri for song in non_downloaded_songs]

    logger.info(f"Downloading {len(missing_song_array)} missing songs")
    downloader_config = Config(urls=missing_song_array, track_artists=False)

    # TODO: Re-enable ProcessInfo after fixing circular imports
    # if self is not None:
    #     process_info = ProcessInfo(self, desc="missing song download", total=1000)
    #     downloader_config.process_info = process_info

    # Create progress callback if task history is available
    task_progress_callback = None
    if hasattr(self, "request") and self.request.id:
        task_history = TaskHistory.objects.filter(task_id=self.request.id).first()
        if task_history:

            def update_task_progress_callback(progress_pct, message):
                task_history.update_progress(progress_pct, message)

            task_progress_callback = update_task_progress_callback

    spotdl_wrapper.execute(downloader_config, task_progress_callback)

    # Don't call recursively if there weren't any songs that definitely should have existed
    if non_downloaded_songs_that_should_exist_count == 0:
        logger.info("All songs marked downloaded that should be!")
        return
    # Queue up next batch after ensuring rate limit has passed
    validate_undownloaded_songs.delay()
