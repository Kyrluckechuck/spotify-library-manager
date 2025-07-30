from typing import AsyncGenerator

import strawberry

from ..graphql_types.models import DownloadStatus
from ..services.event_bus import event_bus


@strawberry.type
class DownloadProgress:
    entity_id: str
    entity_type: str
    progress: float
    status: DownloadStatus
    message: str


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def download_progress(
        self, entity_id: str
    ) -> AsyncGenerator[DownloadProgress, None]:
        async for progress in event_bus.subscribe_to_download_progress(entity_id):
            yield progress

    @strawberry.subscription
    async def all_download_progress(self) -> AsyncGenerator[DownloadProgress, None]:
        async for progress in event_bus.subscribe_to_download_progress():
            yield progress
