# mypy: disable-error-code=attr-defined
from typing import Any, List, Optional, Tuple

from django.db import models

from asgiref.sync import sync_to_async

from library_manager.models import TaskHistory as DjangoTaskHistory

from ..graphql_types.models import EntityType, TaskHistory, TaskStatus, TaskType
from ..types.typing import SupportsId
from .base import BaseService


class TaskHistoryService(BaseService[TaskHistory]):
    def __init__(self) -> None:
        super().__init__()
        self.model = DjangoTaskHistory

    async def get_by_id(self, id: str) -> Optional[TaskHistory]:
        # Not required by API; implement to satisfy linter
        return None

    async def get_connection(
        self,
        first: int = 20,
        after: Optional[str] = None,
        **filters: Any,
    ) -> Tuple[List[TaskHistory], bool, int]:
        status: Optional[TaskStatus] = filters.get("status")
        type: Optional[TaskType] = filters.get("type")
        entity_type: Optional[EntityType] = filters.get("entity_type")
        search: Optional[str] = filters.get("search")
        queryset = self.model.objects.all()

        # Apply filters
        if status:
            status_mapping = {
                TaskStatus.PENDING: "PENDING",
                TaskStatus.RUNNING: "RUNNING",
                TaskStatus.COMPLETED: "COMPLETED",
                TaskStatus.FAILED: "FAILED",
            }
            queryset = queryset.filter(status=status_mapping.get(status, status.value))

        if type:
            type_mapping = {
                TaskType.SYNC: "SYNC",
                TaskType.DOWNLOAD: "DOWNLOAD",
                TaskType.FETCH: "FETCH",
            }
            queryset = queryset.filter(type=type_mapping.get(type, type.value))

        if entity_type:
            entity_mapping = {
                EntityType.ARTIST: "ARTIST",
                EntityType.ALBUM: "ALBUM",
                EntityType.PLAYLIST: "PLAYLIST",
                EntityType.TRACK: "TRACK",
            }
            queryset = queryset.filter(
                entity_type=entity_mapping.get(entity_type, entity_type.value)
            )

        if search:
            queryset = queryset.filter(
                models.Q(task_id__icontains=search)
                | models.Q(entity_id__icontains=search)
            )

        # Apply cursor-based pagination
        if after:
            id_after = self.decode_cursor(after)
            queryset = queryset.filter(id__gt=id_after)

        # Get total count before slicing
        total_count = await sync_to_async(queryset.count)()

        # Get one extra item to determine if there are more pages
        def fetch_items() -> List[DjangoTaskHistory]:
            return list(queryset.order_by("-started_at")[: first + 1])

        items: List[DjangoTaskHistory] = await sync_to_async(fetch_items)()

        has_next_page = len(items) > first
        items = items[:first]  # Remove the extra item

        return (
            [self._to_graphql_type(item) for item in items],
            has_next_page,
            total_count,
        )

    def _to_graphql_type(self, django_task: DjangoTaskHistory) -> TaskHistory:
        # Convert Django model to GraphQL type
        status_mapping = {
            "PENDING": TaskStatus.PENDING,
            "RUNNING": TaskStatus.RUNNING,
            "COMPLETED": TaskStatus.COMPLETED,
            "FAILED": TaskStatus.FAILED,
        }

        type_mapping = {
            "SYNC": TaskType.SYNC,
            "DOWNLOAD": TaskType.DOWNLOAD,
            "FETCH": TaskType.FETCH,
        }

        entity_mapping = {
            "ARTIST": EntityType.ARTIST,
            "ALBUM": EntityType.ALBUM,
            "PLAYLIST": EntityType.PLAYLIST,
        }

        # Extract log messages
        log_messages = []
        if django_task.log_messages:
            # Handle both string and dict formats for backward compatibility
            for log in django_task.log_messages:
                if isinstance(log, dict) and "message" in log:
                    log_messages.append(log["message"])
                elif isinstance(log, str):
                    log_messages.append(log)

        return TaskHistory(
            id=str(django_task.id),
            task_id=django_task.task_id,
            type=type_mapping.get(django_task.type, TaskType.SYNC),
            entity_id=django_task.entity_id,
            entity_type=entity_mapping.get(django_task.entity_type, EntityType.ARTIST),
            status=status_mapping.get(django_task.status, TaskStatus.PENDING),
            started_at=django_task.started_at.isoformat(),
            completed_at=(
                django_task.completed_at.isoformat()
                if django_task.completed_at
                else None
            ),
            duration_seconds=django_task.duration_seconds,
            progress_percentage=django_task.progress_percentage,
            log_messages=log_messages,
        )

    def create_cursor(self, item: SupportsId | TaskHistory) -> str:
        # Prefer string cursor on schema types; BaseService encodes cursor
        return super().create_cursor(item)

    def decode_cursor(self, cursor: str) -> int:
        # Use the shared opaque cursor decoder
        from ..utils.cursor import decode_cursor

        return int(decode_cursor(cursor))

    async def create_task(
        self, task_id: str, task_type: TaskType, entity_id: str, entity_type: EntityType
    ) -> DjangoTaskHistory:
        """Create a new task history record"""
        type_mapping = {
            TaskType.SYNC: "SYNC",
            TaskType.DOWNLOAD: "DOWNLOAD",
            TaskType.FETCH: "FETCH",
        }

        entity_mapping = {
            EntityType.ARTIST: "ARTIST",
            EntityType.ALBUM: "ALBUM",
            EntityType.PLAYLIST: "PLAYLIST",
        }

        task = DjangoTaskHistory(
            task_id=task_id,
            type=type_mapping.get(task_type, "SYNC"),
            entity_id=entity_id,
            entity_type=entity_mapping.get(entity_type, "ARTIST"),
            status="PENDING",
        )
        await sync_to_async(task.save)()
        return task
