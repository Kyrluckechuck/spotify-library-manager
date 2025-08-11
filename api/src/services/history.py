# mypy: disable-error-code=attr-defined
from typing import Any, List, Optional, Tuple

from library_manager.models import DownloadHistory as DjangoDownloadHistory

from ..graphql_types.models import DownloadHistory, DownloadStatus
from .base import BaseService


class DownloadHistoryService(BaseService[DownloadHistory]):
    def __init__(self) -> None:
        super().__init__()
        self.model = DjangoDownloadHistory

    async def get_by_id(self, id: str) -> Optional[DownloadHistory]:
        # Not needed for current API; implement to satisfy linter
        return None

    async def get_connection(
        self,
        first: int = 20,
        after: Optional[str] = None,
        **filters: Any,
    ) -> Tuple[List[DownloadHistory], bool, int]:
        entity_type: Optional[str] = filters.get("entity_type")
        status: Optional[str] = filters.get("status")
        queryset = self.model.objects.all()

        # Apply filters
        if entity_type:
            queryset = queryset.filter(url__contains=entity_type)

        if status:
            if status == "COMPLETED":
                queryset = queryset.filter(completed_at__isnull=False)
            elif status == "IN_PROGRESS":
                queryset = queryset.filter(completed_at__isnull=True, progress__gt=0)
            elif status == "PENDING":
                queryset = queryset.filter(completed_at__isnull=True, progress=0)

        # Apply cursor-based pagination
        if after:
            id_after = self.decode_cursor(after)
            queryset = queryset.filter(id__gt=id_after)

        # Get total count before slicing
        total_count = await queryset.acount()

        # Get one extra item to determine if there are more pages
        items = list(await queryset.order_by("-added_at")[: first + 1].all())

        has_next_page = len(items) > first
        items = items[:first]  # Remove the extra item

        return (
            [self._to_graphql_type(item) for item in items],
            has_next_page,
            total_count,
        )

    def _to_graphql_type(
        self, django_history: DjangoDownloadHistory
    ) -> DownloadHistory:
        # Extract entity type and ID from URL
        url_parts = django_history.url.split(":")
        entity_type = url_parts[1].upper() if len(url_parts) > 1 else "UNKNOWN"
        entity_id = url_parts[2] if len(url_parts) > 2 else django_history.url

        # Determine status
        if django_history.completed_at:
            status = DownloadStatus.COMPLETED
        elif django_history.progress > 0:
            status = DownloadStatus.IN_PROGRESS
        else:
            status = DownloadStatus.PENDING

        return DownloadHistory(
            id=str(django_history.id),
            entity_id=entity_id,
            entity_type=entity_type,
            status=status,
            started_at=django_history.added_at.isoformat(),
            completed_at=(
                django_history.completed_at.isoformat()
                if django_history.completed_at
                else None
            ),
            error_message=None,  # TODO: Add error message support
        )
