import hashlib
from typing import Dict, List, Optional

from django.db.models import QuerySet

from celery.result import AsyncResult

from .models import Artist, TrackedPlaylist

# Celery Task Deduplication Utilities


def generate_task_id(task_name: str, *args, **kwargs) -> str:
    """
    Generate a deterministic task ID based on task name and arguments.

    This allows Celery to deduplicate tasks - if a task with the same ID
    is already queued or running, attempting to queue another will be ignored.

    Args:
        task_name: Name of the Celery task
        *args: Positional arguments to the task
        **kwargs: Keyword arguments to the task

    Returns:
        A unique, deterministic task ID string
    """
    # Create a stable string representation of args/kwargs
    arg_str = f"{task_name}:{args}:{sorted(kwargs.items())}"
    # Hash it to get a reasonable-length ID
    task_hash = hashlib.md5(arg_str.encode()).hexdigest()
    return f"{task_name}-{task_hash[:12]}"


def is_task_pending_or_running(task_id: str) -> bool:
    """
    Check if a task with the given ID is currently pending or running.

    Args:
        task_id: The Celery task ID to check

    Returns:
        True if task is PENDING or STARTED, False otherwise
    """
    result = AsyncResult(task_id)
    return result.state in ["PENDING", "STARTED", "RETRY"]


# Original Huey implementations (commented out)
# def get_all_tasks_with_name(task_name: str) -> List[Task]:
#     potential_tasks: List[Task] = rawHuey.pending()
#     found_tasks: List[Task] = []
#     for potential_task in potential_tasks:
#         if potential_task.name == task_name:
#             found_tasks.append(potential_task)
#     return found_tasks

# def convert_first_task_args_to_list(
#     pending_tasks: List[Task],
# ) -> Union[List[int], List[str]]:
#     pending_args: Union[List[int], List[str]] = []
#     for pending_task in pending_tasks:
#         pending_args.append(pending_task.args[0])
#     return pending_args


def update_tracked_artists_albums(
    already_enqueued_artists: List[int],
    artists_to_enqueue: List[Artist],
    priority: Optional[int] = None,
) -> None:
    # Local import to avoid circular import during module initialization
    from .tasks import fetch_all_albums_for_artist

    for artist in artists_to_enqueue:
        # Use database ID for internal operations
        if artist.id in already_enqueued_artists:
            continue

        # Generate deterministic task ID for deduplication
        task_id = generate_task_id(
            "library_manager.tasks.fetch_all_albums_for_artist", artist.id
        )

        # Skip if task is already queued or running
        if is_task_pending_or_running(task_id):
            continue

        extra_args = {}
        if priority is not None:
            extra_args["priority"] = priority

        # Queue task asynchronously with deterministic ID for deduplication
        fetch_all_albums_for_artist.apply_async(
            args=[artist.id], task_id=task_id, **extra_args
        )


def download_missing_tracked_artists(
    already_enqueued_artists: List[int],
    artists_to_enqueue: List[Artist],
    priority: Optional[int] = None,
) -> None:
    # Local import to avoid circular import during module initialization
    from .tasks import download_missing_albums_for_artist

    for artist in artists_to_enqueue:
        # Use database ID for internal operations
        if artist.id in already_enqueued_artists:
            continue

        # Generate deterministic task ID for deduplication
        task_id = generate_task_id(
            "library_manager.tasks.download_missing_albums_for_artist",
            artist.id,
            delay=5,
        )

        # Skip if task is already queued or running
        if is_task_pending_or_running(task_id):
            continue

        extra_args = {}
        if priority is not None:
            extra_args["priority"] = priority

        # Queue the task asynchronously with deterministic ID for deduplication
        download_missing_albums_for_artist.apply_async(
            args=[artist.id], kwargs={"delay": 5}, task_id=task_id, **extra_args
        )


def download_non_enqueued_playlists(
    already_enqueued_playlists: List[str],
    playlists_to_enqueue: List[TrackedPlaylist],
    priority: Optional[int] = None,
) -> None:
    # Local import to avoid circular import during module initialization
    from .tasks import download_playlist

    for playlist in playlists_to_enqueue:
        if playlist.url in already_enqueued_playlists:
            continue

        # Generate deterministic task ID for deduplication
        task_id = generate_task_id(
            "library_manager.tasks.download_playlist",
            playlist.url,
            tracked=playlist.auto_track_artists,
        )

        # Skip if task is already queued or running
        if is_task_pending_or_running(task_id):
            continue

        extra_args = {}
        if priority is not None:
            extra_args["priority"] = priority

        # Queue the task asynchronously with deterministic ID for deduplication
        download_playlist.apply_async(
            kwargs={
                "playlist_url": playlist.url,
                "tracked": playlist.auto_track_artists,
            },
            task_id=task_id,
            **extra_args,
        )


def enqueue_playlists(
    playlists_to_enqueue: List[TrackedPlaylist], priority: Optional[int] = None
) -> None:
    download_non_enqueued_playlists([], playlists_to_enqueue, priority=priority)


def enqueue_fetch_all_albums_for_artists(
    artists: QuerySet[Artist], extra_args: Optional[dict] = None
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
    artists: QuerySet[Artist], extra_args: Optional[dict] = None
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


def enqueue_batch_artist_operations(
    artists: QuerySet[Artist],
    operations: Optional[List[str]] = None,
    extra_args: Optional[dict] = None,
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
    operation_counts: dict[str, int] = {}

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
        priority: Celery task priority (lower = higher priority)
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
