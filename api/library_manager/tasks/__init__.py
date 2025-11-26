"""Celery tasks for the Spotify library manager.

This package contains all Celery tasks organized by functionality:
- artist: Artist synchronization and fetching
- playlist: Playlist synchronization
- download: Album and song download operations
- maintenance: Cleanup, retry, and validation tasks
- periodic: Scheduled periodic tasks
- core: Shared utilities and helper functions

All tasks are re-exported here for backwards compatibility.
"""

# Re-export artist tasks
from .artist import (
    download_missing_tracked_artists,
    fetch_all_albums_for_artist,
    fetch_all_albums_for_artist_sync,
    update_tracked_artists,
)

# Re-export core utilities
from .core import (
    celery_app,
    check_and_update_progress,
    check_task_cancellation,
    complete_task,
    create_task_history,
    log_memory_usage,
    logger,
    require_download_capability,
    spotdl_wrapper,
    update_task_heartbeat,
    update_task_progress,
)

# Re-export download tasks
from .download import (
    download_album_by_spotify_id,
    download_extra_album_types_for_artist,
    download_missing_albums_for_artist,
    download_playlist,
    download_single_album,
    download_single_track,
)

# Re-export maintenance tasks
from .maintenance import (
    cleanup_celery_history,
    cleanup_stuck_tasks_periodic,
    retry_all_missing_known_songs,
    retry_failed_songs,
    validate_undownloaded_songs,
)

# Re-export periodic tasks
from .periodic import (
    queue_missing_albums_for_tracked_artists,
    sync_tracked_playlists,
)

# Re-export playlist tasks
from .playlist import (
    _sync_tracked_playlist_internal,
    sync_tracked_playlist,
    sync_tracked_playlist_artists,
)

__all__ = [
    # Core utilities
    "celery_app",
    "check_and_update_progress",
    "check_task_cancellation",
    "complete_task",
    "create_task_history",
    "log_memory_usage",
    "logger",
    "require_download_capability",
    "spotdl_wrapper",
    "update_task_heartbeat",
    "update_task_progress",
    # Artist tasks
    "download_missing_tracked_artists",
    "fetch_all_albums_for_artist",
    "fetch_all_albums_for_artist_sync",
    "update_tracked_artists",
    # Playlist tasks
    "_sync_tracked_playlist_internal",
    "sync_tracked_playlist",
    "sync_tracked_playlist_artists",
    # Download tasks
    "download_album_by_spotify_id",
    "download_extra_album_types_for_artist",
    "download_missing_albums_for_artist",
    "download_playlist",
    "download_single_album",
    "download_single_track",
    # Maintenance tasks
    "cleanup_celery_history",
    "cleanup_stuck_tasks_periodic",
    "retry_all_missing_known_songs",
    "retry_failed_songs",
    "validate_undownloaded_songs",
    # Periodic tasks
    "queue_missing_albums_for_tracked_artists",
    "sync_tracked_playlists",
]
