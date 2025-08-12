import logging
import time
import uuid
from typing import Optional, cast

from django.conf import settings
from django.db.models.functions import Now
from django.utils import timezone

import huey.contrib.djhuey as huey  # pylint: disable=no-name-in-module
from downloader.spotdl_wrapper import SpotdlWrapper
from downloader.spotipy_tasks import track_artists_in_playlist
from downloader.utils import sanitize_and_strip_url
from huey import crontab
from huey.api import Task
from huey_monitor.tqdm import ProcessInfo
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

spotdl_wrapper = SpotdlWrapper(Config())


def create_task_history(
    task: Optional[Task] = None,
    task_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    task_name: Optional[str] = None,
) -> TaskHistory:
    """Create a task history record for tracking task execution"""
    if task is not None:
        # Use Huey task context
        entity_type_str = entity_type or "unknown"
        task_id = f"{task_type}-{entity_type_str.lower()}-{entity_id}"
    else:
        # Create task history without Huey context
        task_id = f"{task_name or 'unknown'}-{uuid.uuid4().hex[:8]}"

    # Check if task history already exists for this task
    existing_task = TaskHistory.objects.filter(task_id=task_id).first()
    if existing_task:
        return existing_task

    # Create new task history record
    task_history = TaskHistory(
        task_id=task_id,
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


@huey.task(context=True, priority=3)  # type: ignore[misc]
def fetch_all_albums_for_artist(artist_id: int, task: Task = None) -> None:
    task_history = None
    try:
        # Check if artist exists before proceeding
        try:
            artist = Artist.objects.get(id=artist_id)
        except Artist.DoesNotExist:
            print(f"Artist with ID {artist_id} does not exist. Skipping task.")
            return

        # Create task history record (always create, even without Huey context)
        task_history = create_task_history(
            task=task,
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

        # Check for cancellation before proceeding
        if check_task_cancellation(task_history):
            print(f"Task cancelled for artist {artist.name}")
            return

        downloader_config = Config()
        downloader_config.artist_to_fetch = artist.gid
        downloader_config.urls = []

        if task is not None:
            process_info = ProcessInfo(
                task, desc=f"fetch all albums for artist (artist.gid: {artist.gid})"
            )
            downloader_config.process_info = process_info

        # Check for cancellation before major operation
        if check_and_update_progress(
            task_history, 25.0, "Fetching artist albums from Spotify"
        ):
            print(f"Task cancelled during Spotify fetch for artist {artist.name}")
            return

        spotdl_wrapper.execute(downloader_config)

        # Final cancellation check before completion
        if check_task_cancellation(task_history):
            print(f"Task cancelled before completion for artist {artist.name}")
            return

        complete_task(task_history, success=True)

    except Exception as e:
        if task_history:
            complete_task(task_history, success=False, error_message=str(e))
        raise


@huey.task(context=True, priority=1, retries=2, retry_delay=30)  # type: ignore[misc]
def download_missing_albums_for_artist(
    artist_id: int, task: Task = None, delay: int = 0
) -> None:
    task_history = None
    try:
        # Add delay (if applicable) to reduce chance of flagging when backfilling library
        time.sleep(delay)

        # Check if artist exists before proceeding
        try:
            artist = Artist.objects.get(id=artist_id)
        except Artist.DoesNotExist:
            print(f"Artist with ID {artist_id} does not exist. Skipping task.")
            return

        # Create task history record
        if task is not None:
            task_history = create_task_history(task, "DOWNLOAD", artist.gid, "ARTIST")
            update_task_progress(
                task_history, 0.0, f"Starting download for artist {artist.name}"
            )

        missing_albums = Album.objects.filter(
            artist=artist,
            downloaded=False,
            wanted=True,
            album_type__in=ALBUM_TYPES_TO_DOWNLOAD,
        ).exclude(album_group__in=ALBUM_GROUPS_TO_IGNORE)
        print(
            f"missing albums search for artist {artist.gid} found {missing_albums.count()}"
        )

        if task_history:
            update_task_progress(
                task_history, 25.0, f"Found {missing_albums.count()} missing albums"
            )

        downloader_config = Config()
        if task is not None and task_history:
            process_info = ProcessInfo(
                task,
                desc=f"artist missing album download (artist.gid: {artist.gid})",
                total=1000,
            )
            downloader_config.process_info = process_info
            update_task_progress(task_history, 50.0, "Preparing download configuration")

        downloader_config.urls = (
            []
        )  # This must be reset or it will persist between runs
        if missing_albums.count() > 0:
            for missing_album in missing_albums:
                downloader_config.urls.append(missing_album.spotify_uri)

            print(
                f"missing albums search for artist {artist.gid} kicking off {len(downloader_config.urls)}"
            )
            if task_history:
                update_task_progress(
                    task_history,
                    75.0,
                    f"Downloading {len(downloader_config.urls)} albums",
                )
            spotdl_wrapper.execute(downloader_config)
        else:
            print(
                f"missing albums search for artist {artist.gid} is skipping since there are none missing"
            )
            if task_history:
                update_task_progress(
                    task_history, 100.0, "No missing albums to download"
                )

        artist.last_synced_at = Now()
        artist.save()

        if task_history:
            complete_task(task_history, success=True)

    except Exception as e:
        logger = logging.getLogger("api.library_manager")
        logger.error("Error in sync_tracked_playlist_internal: %s", e, exc_info=True)
        if task_history:
            complete_task(task_history, success=False, error_message=str(e))
        raise


def _sync_tracked_playlist_internal(
    tracked_playlist: TrackedPlaylist, task: Task = None
) -> None:
    """Internal function that does the actual sync work"""
    task_history = None
    try:
        # Create task history record for the sync operation
        task_history = create_task_history(
            task=task,
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
        priority = task.priority if task else 2
        helpers.enqueue_playlists([tracked_playlist], priority=priority)

        # Mark as completed since the sync operation is done (download is queued separately)
        complete_task(task_history, success=True)

    except Exception as e:
        if task_history:
            complete_task(task_history, success=False, error_message=str(e))
        raise


@huey.task(context=True, priority=2, retries=2, retry_delay=30)  # type: ignore[misc]
def sync_tracked_playlist(tracked_playlist: TrackedPlaylist, task: Task = None) -> None:
    """Huey task wrapper for sync_tracked_playlist"""
    _sync_tracked_playlist_internal(tracked_playlist, task)


@huey.task(context=True, priority=2, retries=2, retry_delay=30)  # type: ignore[misc]
def download_playlist(
    playlist_url: str,
    tracked: bool = True,
    force_playlist_resync: bool = False,
    task: Task = None,
) -> None:
    task_history = None
    try:
        playlist_url = sanitize_and_strip_url(playlist_url)

        # Extract playlist ID from URL for task history
        playlist_id = (
            playlist_url.split(":")[-1] if ":" in playlist_url else playlist_url
        )

        # Create task history record (always create, even without Huey context)
        task_history = create_task_history(
            task=task,
            task_type="DOWNLOAD",
            entity_id=playlist_id,
            entity_type="PLAYLIST",
            task_name="download_playlist",
        )
        update_task_progress(
            task_history, 0.0, f"Starting playlist download: {playlist_url}"
        )
        # Mark as running
        task_history.status = "RUNNING"
        task_history.save()

        downloader_config = Config(
            urls=[playlist_url],
            track_artists=tracked,
            force_playlist_resync=force_playlist_resync,
        )

        if task is not None:
            process_info = ProcessInfo(task, desc="playlist download", total=1000)
            downloader_config.process_info = process_info
        update_task_progress(task_history, 50.0, "Downloading playlist tracks")

        spotdl_wrapper.execute(downloader_config)

        complete_task(task_history, success=True)

    except Exception as e:
        if task_history:
            complete_task(task_history, success=False, error_message=str(e))
        raise


@huey.task(context=True, priority=0, retries=2, retry_delay=30)  # type: ignore[misc]
def retry_all_missing_known_songs(task: Task = None) -> None:
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
        print("All songs downloaded, exiting missing known song loop!")
        return

    failed_song_array = [song.spotify_uri for song in missing_known_songs_list]

    print(f"Downloading {len(failed_song_array)} missing songs")
    downloader_config = Config(urls=failed_song_array, track_artists=False)

    if task is not None:
        process_info = ProcessInfo(
            task, desc="missing/failed song download", total=1000
        )
        downloader_config.process_info = process_info
    spotdl_wrapper.execute(downloader_config)

    # Queue up next batch after ensuring rate limit has passed
    retry_all_missing_known_songs.schedule(delay=30)


@huey.task(context=True, priority=3, retries=2, retry_delay=30)  # type: ignore[misc]
def download_extra_album_types_for_artist(artist_id: int, task: Task = None) -> None:
    # Check if artist exists before proceeding
    try:
        artist = Artist.objects.get(id=artist_id)
    except Artist.DoesNotExist:
        print(f"Artist with ID {artist_id} does not exist. Skipping task.")
        return
    missing_albums = Album.objects.filter(
        artist=artist,
        downloaded=False,
        wanted=True,
        album_group__in=ALBUM_GROUPS_TO_IGNORE,
    )
    print(
        f"extra album missing albums search for artist {artist.gid} found {missing_albums.count()}"
    )
    downloader_config = Config()
    if task is not None:
        process_info = ProcessInfo(
            task,
            desc=f"extra album artist missing album download (artist.gid: {artist.gid})",
            total=1000,
        )
        downloader_config.process_info = process_info
    downloader_config.urls = []  # This must be reset or it will persist between runs
    if missing_albums.count() > 0:
        for missing_album in missing_albums:
            downloader_config.urls.append(missing_album.spotify_uri)

        print(
            f"extra album missing albums search for artist {artist.gid} kicking off {len(downloader_config.urls)}"
        )
        spotdl_wrapper.execute(downloader_config)
    else:
        print(
            f"extra album missing albums search for artist {artist.gid} is skipping since there are none missing"
        )
    artist.last_synced_at = Now()
    artist.save()


@huey.task(context=True, priority=3)  # type: ignore[misc]
def sync_tracked_playlist_artists(playlist: TrackedPlaylist, task: Task = None) -> None:
    # Given a playlist, track the artists without actually downloading the playlist (potentially, again)
    track_artists_in_playlist(playlist.url, task)


@huey.periodic_task(crontab(minute="0", hour="*/8"), priority=1, context=True)  # type: ignore[misc]
def update_tracked_artists(task: Task = None) -> None:
    all_tracked_artists = Artist.objects.filter(tracked=True).order_by(
        "last_synced_at", "added_at", "id"
    )
    existing_tasks = helpers.get_all_tasks_with_name("fetch_all_albums_for_artist")
    already_enqueued_artists = helpers.convert_first_task_args_to_list(existing_tasks)
    # Convert to List[int] since artist IDs are integers
    artist_ids = (
        [int(id) for id in already_enqueued_artists]
        if isinstance(already_enqueued_artists, list)
        else []
    )
    helpers.update_tracked_artists_albums(
        artist_ids, list(all_tracked_artists), priority=task.priority
    )


# Severely throttling automatic playlist download for tracked artists for the time being;
# There is a high likelyhood of being flagged due to high usage at the moment and a new scalable solution needs to be investigated.
@huey.periodic_task(crontab(minute="45", hour="*/8"), priority=0, context=True)  # type: ignore[misc]
def download_missing_tracked_artists(task: Task = None) -> None:
    if settings.disable_missing_tracked_artist_download:
        print(
            "Skipping queued missing tracked artists due to disable_missing_tracked_artist_download setting"
        )
        return

    from datetime import timedelta

    twelve_hours_ago = timezone.now() - timedelta(hours=12)
    recently_downloaded_songs = DownloadHistory.objects.filter(
        added_at__gte=twelve_hours_ago
    )
    if recently_downloaded_songs.count() > 250:
        print(
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
    existing_tasks = helpers.get_all_tasks_with_name(
        "download_missing_albums_for_artist"
    )
    already_enqueued_artists = helpers.convert_first_task_args_to_list(existing_tasks)
    # Convert to List[int] since artist IDs are integers
    artist_ids = (
        [int(id) for id in already_enqueued_artists]
        if isinstance(already_enqueued_artists, list)
        else []
    )
    helpers.download_missing_tracked_artists(
        artist_ids, list(all_tracked_artists), priority=task.priority
    )


@huey.periodic_task(crontab(minute="0", hour="*/4"), priority=1, context=True)  # type: ignore[misc]
def sync_tracked_playlists(task: Task = None) -> None:
    all_enabled_playlists = TrackedPlaylist.objects.filter(enabled=True).order_by(
        "last_synced_at", "id"
    )
    helpers.enqueue_playlists(list(all_enabled_playlists), priority=task.priority)


@huey.periodic_task(crontab(minute="0", hour="6"), priority=10)  # type: ignore[misc]
def cleanup_huey_history() -> None:
    helpers.cleanup_huey_history()


@huey.periodic_task(crontab(minute="*/5"), priority=5)  # type: ignore[misc]  # Every 5 minutes
def cleanup_stuck_tasks_periodic() -> None:
    """Periodically clean up stuck tasks and stale artist references"""
    from library_manager.models import TaskHistory

    stuck_count = TaskHistory.cleanup_stuck_tasks()
    if stuck_count > 0:
        print(f"Cleaned up {stuck_count} stuck task(s)")

    # Clean up stale artist references in Huey queue
    from huey.contrib.djhuey import HUEY

    from library_manager.models import Artist

    pending_tasks = HUEY.pending()
    stale_tasks = []

    for task in pending_tasks:
        if task.name in [
            "fetch_all_albums_for_artist",
            "download_missing_albums_for_artist",
            "download_extra_album_types_for_artist",
        ]:
            if task.args and len(task.args) > 0:
                artist_id = task.args[0]
                if not Artist.objects.filter(id=artist_id).exists():
                    stale_tasks.append(task)

    if stale_tasks:
        print(f"Found {len(stale_tasks)} stale tasks for non-existent artists")
        # Note: We can't easily remove individual tasks from Huey queue
        # The queue will be cleared when the worker restarts or manually flushed


@huey.task(context=True, priority=0, retries=2, retry_delay=30)  # type: ignore[misc]
def validate_undownloaded_songs(
    task: Task = None,
) -> None:
    non_downloaded_songs_that_should_exist = Song.objects.filter(
        bitrate__gt=0, unavailable=False, downloaded=False
    ).order_by("created_at")[:50]
    non_downloaded_songs_that_maybe_should_exist = Song.objects.filter(
        bitrate__gt=0, unavailable=True, downloaded=False
    ).order_by("created_at")[:50]

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
        print("All songs marked downloaded that should be!")
        return

    missing_song_array = [song.spotify_uri for song in non_downloaded_songs]

    print(f"Downloading {len(missing_song_array)} missing songs")
    downloader_config = Config(urls=missing_song_array, track_artists=False)

    if task is not None:
        process_info = ProcessInfo(task, desc="missing song download", total=1000)
        downloader_config.process_info = process_info
    spotdl_wrapper.execute(downloader_config)

    # Don't call recursively if there weren't any songs that definitely should have existed
    if non_downloaded_songs_that_should_exist_count == 0:
        print("All songs marked downloaded that should be!")
        return
    # Queue up next batch after ensuring rate limit has passed
    validate_undownloaded_songs()
