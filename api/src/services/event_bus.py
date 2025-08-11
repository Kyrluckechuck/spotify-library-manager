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
            # TODO: Extract playlist ID from task args
        elif "album download" in desc:
            entity_type = "ALBUM"
            # TODO: Extract album ID from task args

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
