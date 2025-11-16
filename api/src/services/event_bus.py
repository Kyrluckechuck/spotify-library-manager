import asyncio
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional

from ..graphql_types.models import DownloadProgress


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
