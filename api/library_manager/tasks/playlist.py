"""Playlist tasks for the Spotify library manager."""

from typing import Any, Optional

from celery_app import app as celery_app
from downloader.spotipy_tasks import track_artists_in_playlist

from .. import helpers
from ..models import TrackedPlaylist
from .core import complete_task, create_task_history, logger, update_task_progress


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


@celery_app.task(bind=True, name="library_manager.tasks.sync_tracked_playlist")
def sync_tracked_playlist(
    self: Any, playlist_id: int, task_id: Optional[str] = None
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


@celery_app.task(bind=True, name="library_manager.tasks.sync_tracked_playlist_artists")
def sync_tracked_playlist_artists(
    self: Any, playlist_id: int, task_id: Optional[str] = None
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
