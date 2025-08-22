from typing import Dict, List, Optional, Union

from django.db import connection
from django.db.models import QuerySet

from huey.api import Task
from huey.contrib.djhuey import HUEY as rawHuey

from .models import Artist, TrackedPlaylist


def get_all_tasks_with_name(task_name: str) -> List[Task]:
    potential_tasks: List[Task] = rawHuey.pending()

    found_tasks: List[Task] = []

    for potential_task in potential_tasks:
        if potential_task.name == task_name:
            found_tasks.append(potential_task)

    return found_tasks


def convert_first_task_args_to_list(
    pending_tasks: List[Task],
) -> Union[List[int], List[str]]:
    pending_args: Union[List[int], List[str]] = []

    for pending_task in pending_tasks:
        pending_args.append(pending_task.args[0])

    return pending_args


def update_tracked_artists_albums(
    already_enqueued_artists: List[int],
    artists_to_enqueue: List[Artist],
    priority: Optional[int] = None,
) -> None:
    for artist in artists_to_enqueue:
        # Use database ID for internal operations
        if artist.id in already_enqueued_artists:
            continue

        extra_args = {}
        if priority is not None:
            extra_args["priority"] = priority
        # Local import to avoid circular import during module initialization
        from .tasks import fetch_all_albums_for_artist

        # Pass database ID, not gid
        fetch_all_albums_for_artist(artist.id, **extra_args)


def download_missing_tracked_artists(
    already_enqueued_artists: List[int],
    artists_to_enqueue: List[Artist],
    priority: Optional[int] = None,
) -> None:
    for artist in artists_to_enqueue:
        # Use database ID for internal operations
        if artist.id in already_enqueued_artists:
            continue

        extra_args = {
            # Delay album downloads for the artists for 5 seconds (once they begin)
            "delay": 5
        }

        if priority is not None:
            extra_args["priority"] = priority
        # Local import to avoid circular import during module initialization
        from .tasks import download_missing_albums_for_artist

        # Pass database ID, not gid
        download_missing_albums_for_artist(artist.id, **extra_args)


def download_non_enqueued_playlists(
    already_enqueued_playlists: List[str],
    playlists_to_enqueue: List[TrackedPlaylist],
    priority: Optional[int] = None,
) -> None:
    for playlist in playlists_to_enqueue:
        if playlist.url in already_enqueued_playlists:
            continue

        extra_args = {}
        if priority is not None:
            extra_args["priority"] = priority
        # Local import to avoid circular import during module initialization
        from .tasks import download_playlist

        download_playlist(
            playlist_url=playlist.url, tracked=playlist.auto_track_artists, **extra_args
        )


def enqueue_playlists(
    playlists_to_enqueue: List[TrackedPlaylist], priority: Optional[int] = None
) -> None:
    existing_tasks = get_all_tasks_with_name("download_playlist")
    already_enqueued_playlists = convert_first_task_args_to_list(existing_tasks)
    # Convert to List[str] since playlist URLs are strings
    playlist_urls = (
        [str(url) for url in already_enqueued_playlists]
        if isinstance(already_enqueued_playlists, list)
        else []
    )
    download_non_enqueued_playlists(
        playlist_urls, playlists_to_enqueue, priority=priority
    )


def enqueue_fetch_all_albums_for_artists(
    artists: QuerySet[Artist], extra_args: dict = None
) -> None:
    """Enqueue fetch_all_albums_for_artist task for multiple artists."""
    if extra_args is None:
        extra_args = {}

    # Track already enqueued artists to avoid duplicates
    already_enqueued_artists = set()

    for artist in artists:
        # Use database ID for internal operations
        if artist.id in already_enqueued_artists:
            continue
        already_enqueued_artists.add(artist.id)

        # Pass database ID, not gid
        from .tasks import fetch_all_albums_for_artist

        fetch_all_albums_for_artist(artist.id, **extra_args)


def enqueue_download_missing_albums_for_artists(
    artists: QuerySet[Artist], extra_args: dict = None
) -> None:
    """Enqueue download_missing_albums_for_artist task for multiple artists."""
    if extra_args is None:
        extra_args = {}

    # Track already enqueued artists to avoid duplicates
    already_enqueued_artists = set()

    for artist in artists:
        # Use database ID for internal operations
        if artist.id in already_enqueued_artists:
            continue
        already_enqueued_artists.add(artist.id)

        # Pass database ID, not gid
        from .tasks import download_missing_albums_for_artist

        download_missing_albums_for_artist(artist.id, **extra_args)


def cleanup_huey_history() -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE huey_monitor_taskmodel SET parent_task_id = NULL, state_id = NULL WHERE create_dt < DATETIME('now', '-3 day');"
        )
        cursor.execute(
            "DELETE FROM huey_monitor_signalinfomodel WHERE create_dt < DATETIME('now', '-4 day');"
        )
        cursor.execute(
            "DELETE FROM huey_monitor_taskmodel WHERE create_dt < DATETIME('now', '-4 day');"
        )
        cursor.execute("VACUUM;")


def enqueue_batch_artist_operations(
    artists: QuerySet[Artist], operations: List[str] = None, extra_args: dict = None
) -> Dict[str, int]:
    """
    Enqueue multiple operations for multiple artists in batch.

    Args:
        artists: QuerySet of artists to process
        operations: List of operations to perform (e.g., ['fetch', 'download'])
        extra_args: Additional arguments to pass to operations

    Returns:
        Dict with operation counts
    """
    if extra_args is None:
        extra_args = {}

    if operations is None:
        operations = ["fetch", "download"]

    # Track already enqueued artists to avoid duplicates
    already_enqueued_artists = set()
    operation_counts = {}

    for artist in artists:
        # Use database ID for internal operations
        if artist.id in already_enqueued_artists:
            continue
        already_enqueued_artists.add(artist.id)

        # Enqueue operations based on artist status
        if "fetch" in operations:
            from .tasks import fetch_all_albums_for_artist

            fetch_all_albums_for_artist(artist.id, **extra_args)
            operation_counts["fetch"] = operation_counts.get("fetch", 0) + 1

        if "download" in operations and artist.tracked:
            from .tasks import download_missing_albums_for_artist

            download_missing_albums_for_artist(artist.id, **extra_args)
            operation_counts["download"] = operation_counts.get("download", 0) + 1

    return operation_counts


def enqueue_priority_artist_operations(
    artists: QuerySet[Artist], priority: int = 5, max_concurrent: int = 10
) -> Dict[str, int]:
    """
    Enqueue high-priority operations for artists with rate limiting.

    Args:
        artists: QuerySet of artists to process
        priority: Huey task priority (lower = higher priority)
        max_concurrent: Maximum concurrent operations

    Returns:
        Dict with operation counts
    """
    extra_args = {"priority": priority}

    # Limit concurrent operations
    limited_artists = artists[:max_concurrent]

    return enqueue_batch_artist_operations(
        limited_artists, operations=["fetch", "download"], extra_args=extra_args
    )


def enqueue_artist_sync_with_download(
    artists: QuerySet[Artist], auto_download: bool = True, delay_seconds: int = 0
) -> Dict[str, int]:
    """
    Enqueue artist sync operations with optional automatic download.

    Args:
        artists: QuerySet of artists to sync
        auto_download: Whether to automatically download missing albums
        delay_seconds: Delay between operations to avoid rate limiting

    Returns:
        Dict with operation counts
    """
    extra_args = {"delay": delay_seconds}

    operations = ["fetch"]
    if auto_download:
        operations.append("download")

    return enqueue_batch_artist_operations(
        artists, operations=operations, extra_args=extra_args
    )
