"""Maintenance tasks for the Spotify library manager."""

from typing import Any, Optional

from celery_app import app as celery_app
from lib.config_class import Config

from ..models import Song, TaskHistory
from .core import logger, require_download_capability, spotdl_wrapper


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 30},
    name="library_manager.tasks.retry_all_missing_known_songs",
)
def retry_all_missing_known_songs(self: Any, task_id: Optional[str] = None) -> None:
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

    # Create progress callback if task history is available
    task_progress_callback = None
    if hasattr(self, "request") and self.request.id:
        task_history = TaskHistory.objects.filter(task_id=self.request.id).first()
        if task_history:
            # Capture task_history in closure to avoid cell-var-from-loop
            captured_task_history = task_history

            def update_task_progress_callback(
                progress_pct: float, message: str
            ) -> None:
                captured_task_history.update_progress(progress_pct)

            task_progress_callback = update_task_progress_callback

    spotdl_wrapper.execute(downloader_config, task_progress_callback)

    # Queue up next batch after ensuring rate limit has passed
    retry_all_missing_known_songs.apply_async(countdown=30)


@celery_app.task(
    bind=True, name="library_manager.tasks.cleanup_stuck_tasks_periodic"
)  # Scheduled via Celery Beat - Every 5 minutes
def cleanup_stuck_tasks_periodic(self: Any) -> None:
    """Periodically clean up stuck tasks and stale artist references"""
    from library_manager.models import TaskHistory

    stuck_count = TaskHistory.cleanup_stuck_tasks()
    if stuck_count > 0:
        logger.info(f"Cleaned up {stuck_count} stuck task(s)")

    # Note: Celery task queue cleanup is handled by the task revocation above
    # Additional queue-level cleanup can be added here if needed


@celery_app.task(
    bind=True, name="library_manager.tasks.cleanup_celery_history"
)  # Scheduled via Celery Beat - Daily at 6 AM
def cleanup_celery_history(self: Any, days_to_keep: int = 30) -> None:
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
    self: Any,
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

    # Create progress callback if task history is available
    task_progress_callback = None
    if hasattr(self, "request") and self.request.id:
        task_history = TaskHistory.objects.filter(task_id=self.request.id).first()
        if task_history:
            # Capture task_history in closure to avoid cell-var-from-loop
            captured_task_history = task_history

            def update_task_progress_callback(
                progress_pct: float, message: str
            ) -> None:
                captured_task_history.update_progress(progress_pct)

            task_progress_callback = update_task_progress_callback

    spotdl_wrapper.execute(downloader_config, task_progress_callback)

    # Don't call recursively if there weren't any songs that definitely should have existed
    if non_downloaded_songs_that_should_exist_count == 0:
        logger.info("All songs marked downloaded that should be!")
        return
    # Queue up next batch after ensuring rate limit has passed
    validate_undownloaded_songs.delay()


@celery_app.task(
    bind=True, name="library_manager.tasks.retry_failed_songs"
)  # Scheduled via Celery Beat - Every 6 hours
def retry_failed_songs(self: Any) -> None:
    """
    Periodically retry downloading songs that have previously failed.

    Uses a priority queue approach: songs with fewer failures are retried first.
    As songs fail and their failed_count increments, they naturally move to the
    back of the queue, ensuring fair rotation over time.

    Processes up to 100 songs per run, ordered by:
    1. failed_count ASC (fewer failures = higher priority)
    2. created_at ASC (older songs = higher priority within same failure count)

    Songs with >10 failures are skipped (likely permanently unavailable).
    """
    try:
        logger.info("Starting periodic retry of failed songs")

        # Check authentication before proceeding
        require_download_capability()

        # Find songs that have failed but might succeed on retry
        # Priority: songs with fewer failures first
        failed_songs = Song.objects.filter(
            downloaded=False,
            failed_count__gt=0,
            failed_count__lte=10,  # Skip songs that have failed too many times
        ).order_by("failed_count", "created_at")[:100]

        if not failed_songs.exists():
            logger.info("No failed songs to retry")
            return

        song_count = failed_songs.count()
        logger.info(
            f"Found {song_count} failed songs to retry " f"(failed_count range: 1-10)"
        )

        # Build list of Spotify URIs to retry
        song_uris = [song.spotify_uri for song in failed_songs]

        # Log some stats about what we're retrying
        failure_counts: dict[int, int] = {}
        for song in failed_songs:
            failure_counts[song.failed_count] = (
                failure_counts.get(song.failed_count, 0) + 1
            )
        logger.info(f"Retry batch failure count distribution: {failure_counts}")

        # Download the songs
        downloader_config = Config(urls=song_uris, track_artists=False)

        # Create progress callback if task history is available
        task_progress_callback = None
        if hasattr(self, "request") and self.request.id:
            task_history = TaskHistory.objects.filter(task_id=self.request.id).first()
            if task_history:
                # Capture task_history in closure to avoid cell-var-from-loop
                captured_task_history = task_history

                def update_task_progress_callback(
                    progress_pct: float, message: str
                ) -> None:
                    captured_task_history.update_progress(progress_pct)

                task_progress_callback = update_task_progress_callback

        logger.info(f"Starting download retry for {song_count} songs")
        spotdl_wrapper.execute(downloader_config, task_progress_callback)
        logger.info(f"Completed retry attempt for {song_count} songs")

    except Exception as e:
        logger.error(f"Error in retry_failed_songs: {e}", exc_info=True)
