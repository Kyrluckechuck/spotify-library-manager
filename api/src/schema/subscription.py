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
            # progress is a GQL type already; coerce to the local schema type
            yield DownloadProgress(
                entity_id=progress.entity_id,
                entity_type=progress.entity_type,
                progress=progress.progress,
                status=progress.status,
                message=progress.message or "",
            )

    @strawberry.subscription
    async def all_download_progress(self) -> AsyncGenerator[DownloadProgress, None]:
        async for progress in event_bus.subscribe_to_download_progress():
            yield DownloadProgress(
                entity_id=progress.entity_id,
                entity_type=progress.entity_type,
                progress=progress.progress,
                status=progress.status,
                message=progress.message or "",
            )
