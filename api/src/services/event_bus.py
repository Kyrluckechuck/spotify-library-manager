from typing import AsyncGenerator, Optional, Any
import asyncio
from huey_monitor.tqdm import ProcessInfo
from ..types.models import DownloadProgress, DownloadStatus

class EventBus:
    _instance: Optional['EventBus'] = None
    _subscribers: dict = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._subscribers = {}
        return cls._instance

    def update_progress(self, process_info: ProcessInfo):
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
            status=DownloadStatus.IN_PROGRESS if process_info.percentage < 100 else DownloadStatus.COMPLETED,
            message=desc
        )

        # Notify subscribers
        for queue in self._subscribers.values():
            queue.put_nowait(progress)

    async def subscribe_to_download_progress(
        self,
        entity_id: Optional[str] = None
    ) -> AsyncGenerator[DownloadProgress, None]:
        queue = asyncio.Queue()
        subscriber_id = id(queue)
        self._subscribers[subscriber_id] = queue

        try:
            while True:
                progress = await queue.get()
                if entity_id is None or progress.entity_id == entity_id:
                    yield progress
        finally:
            del self._subscribers[subscriber_id]

event_bus = EventBus() 