import asyncio
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional

from ..graphql_types.models import DownloadProgress, DownloadStatus


# Mock ProcessInfo class since django-huey-monitor might not be available
class ProcessInfo:
    def __init__(
        self, task: Any | None = None, desc: str | None = None, percentage: int = 0
    ):
        self.task = task
        self.desc = desc
        self.percentage = percentage


class EventBus:
    _instance: Optional["EventBus"] = None
    _subscribers: Dict[str, List[Callable]] = {}
    _download_subscribers: Dict[int, asyncio.Queue] = {}

    def __new__(cls) -> "EventBus":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._subscribers = {}
            cls._instance._download_subscribers = {}
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton for testing purposes."""
        cls._instance = None

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Subscribe to an event type."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        # Prevent duplicate handlers
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """Unsubscribe from an event type."""
        if event_type in self._subscribers:
            if handler in self._subscribers[event_type]:
                self._subscribers[event_type].remove(handler)
            # Remove empty event lists
            if not self._subscribers[event_type]:
                del self._subscribers[event_type]

    async def publish(self, event_type: str, data: Any = None) -> None:
        """Publish an event to all subscribers."""
        if event_type in self._subscribers:
            for handler in self._subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    # Log error but don't stop other handlers
                    print(f"Error in event handler: {e}")

    def update_progress(self, process_info: ProcessInfo) -> None:
        """Called by the task monitor when progress updates"""
        if not process_info or not process_info.task:
            return

        # Extract entity info from task description
        # Example: "artist missing album download (artist.id: 123)"
        desc = process_info.desc or ""
        entity_type = "UNKNOWN"
        entity_id = "unknown"

        if "artist.id:" in desc:
            entity_type = "ARTIST"
            entity_id = desc.split("artist.id:")[-1].strip().strip(")")
        elif "playlist download" in desc:
            entity_type = "PLAYLIST"
            # Attempt to extract playlist ID from task args (first arg is the URL)
            try:
                if process_info.task and getattr(process_info.task, "args", None):
                    first_arg = process_info.task.args[0]
                    if isinstance(first_arg, str) and first_arg:
                        # Expect formats like "spotify:playlist:<id>" or full URLs
                        if ":" in first_arg:
                            entity_id = first_arg.split(":")[-1]
                        else:
                            # Fallback: last path segment
                            entity_id = first_arg.rstrip("/").split("/")[-1]
            except Exception:
                # Best-effort only; leave default on failure
                pass
        elif "album download" in desc:
            entity_type = "ALBUM"
            # Attempt to extract album ID from task args (first arg is the URL/URI)
            try:
                if process_info.task and getattr(process_info.task, "args", None):
                    first_arg = process_info.task.args[0]
                    if isinstance(first_arg, str) and first_arg:
                        # Handle Spotify URI format: "spotify:album:<id>"
                        if first_arg.startswith("spotify:album:"):
                            entity_id = first_arg.split(":")[-1]
                        # Handle URL format: extract last path segment
                        elif "/" in first_arg:
                            entity_id = first_arg.rstrip("/").split("/")[-1]
                        else:
                            # Direct ID
                            entity_id = first_arg
            except Exception:
                # Best-effort only; leave default on failure
                pass

        progress = DownloadProgress(
            entity_id=entity_id,
            entity_type=entity_type,
            progress=process_info.percentage / 100.0,
            status=(
                DownloadStatus.IN_PROGRESS
                if process_info.percentage < 100
                else DownloadStatus.COMPLETED
            ),
            message=desc,
        )

        # Notify subscribers
        for queue in self._download_subscribers.values():
            queue.put_nowait(progress)

    async def subscribe_to_download_progress(
        self, entity_id: Optional[str] = None
    ) -> AsyncGenerator[DownloadProgress, None]:
        queue: asyncio.Queue = asyncio.Queue()
        subscriber_id = id(queue)
        self._download_subscribers[subscriber_id] = queue

        try:
            while True:
                progress = await queue.get()
                if entity_id is None or progress.entity_id == entity_id:
                    yield progress
        finally:
            del self._download_subscribers[subscriber_id]


event_bus = EventBus()
