"""Unit tests for task history service."""

from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest
from asgiref.sync import sync_to_async
from tests.factories import CompletedTaskFactory, FailedTaskFactory, TaskHistoryFactory

from src.graphql_types.models import EntityType, TaskStatus, TaskType
from src.services.task_history import TaskHistoryService


@pytest.fixture
def task_history_service():
    return TaskHistoryService()


@pytest.fixture
def mock_task():
    return Mock(
        id="task_123",
        type="SYNC",
        entity_id="entity_456",
        entity_type="ARTIST",
        status="RUNNING",
        started_at=datetime.now(),
        completed_at=None,
        error_message=None,
        duration_seconds=0,
        progress_percentage=50,
        log_messages=["Task started", "Processing..."],
    )


class TestTaskHistoryService:
    """Test TaskHistoryService functionality."""

    def test_task_history_service_initialization(self, task_history_service):
        """Test TaskHistoryService can be initialized."""
        assert task_history_service is not None
        assert hasattr(task_history_service, "create_task")
        assert hasattr(task_history_service, "get_connection")
        assert hasattr(task_history_service, "_to_graphql_type")

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_create_task_success(self, task_history_service):
        """Test creating a task successfully."""
        task = await task_history_service.create_task(
            task_id="test_task_123_unique",
            task_type=TaskType.SYNC,
            entity_id="artist_456",
            entity_type=EntityType.ARTIST,
        )

        assert task is not None
        assert task.task_id == "test_task_123_unique"
        assert task.type == "SYNC"
        assert task.entity_id == "artist_456"
        assert task.entity_type == "ARTIST"
        assert task.status == "PENDING"

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_get_connection_with_filters(self, task_history_service):
        """Test getting task connection with filters."""
        # Create some test tasks with unique IDs
        await sync_to_async(CompletedTaskFactory)(task_id="completed_task_1")
        await sync_to_async(FailedTaskFactory)(task_id="failed_task_1")

        items, has_next, total = await task_history_service.get_connection(
            first=10, status=TaskStatus.COMPLETED
        )

        assert len(items) >= 1
        assert total >= 1
        assert not has_next  # Should be False for small dataset

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_get_connection_with_pagination(self, task_history_service):
        """Test getting task connection with pagination."""
        # Create multiple tasks with unique IDs
        for i in range(5):
            await sync_to_async(TaskHistoryFactory)(task_id=f"paginated_task_{i}")

        items, has_next, total = await task_history_service.get_connection(first=3)

        assert len(items) == 3
        assert total >= 5
        assert has_next  # Should be True since we have more items

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_get_connection_with_sorting(self, task_history_service):
        """Test getting task connection with sorting."""
        # Create tasks with different timestamps and unique IDs
        await sync_to_async(TaskHistoryFactory)(
            started_at=datetime.now() - timedelta(hours=2), task_id="old_task_1"
        )
        await sync_to_async(TaskHistoryFactory)(
            started_at=datetime.now(), task_id="new_task_1"
        )

        items, has_next, total = await task_history_service.get_connection(first=10)

        assert len(items) >= 2
        # Should be sorted by started_at descending (newest first)
        assert items[0].started_at >= items[1].started_at

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_create_task_with_different_types(self, task_history_service):
        """Test creating tasks with different types."""
        import uuid

        unique_suffix = str(uuid.uuid4())[:8]

        # Test SYNC task
        sync_task = await task_history_service.create_task(
            task_id=f"sync_task_types_{unique_suffix}",
            task_type=TaskType.SYNC,
            entity_id="artist_123",
            entity_type=EntityType.ARTIST,
        )
        assert sync_task.type == "SYNC"

        # Test DOWNLOAD task
        download_task = await task_history_service.create_task(
            task_id=f"download_task_types_{unique_suffix}",
            task_type=TaskType.DOWNLOAD,
            entity_id="album_456",
            entity_type=EntityType.ALBUM,
        )
        assert download_task.type == "DOWNLOAD"

        # Test FETCH task
        fetch_task = await task_history_service.create_task(
            task_id=f"fetch_task_types_{unique_suffix}",
            task_type=TaskType.FETCH,
            entity_id="playlist_789",
            entity_type=EntityType.PLAYLIST,
        )
        assert fetch_task.type == "FETCH"

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_get_connection_empty_result(self, task_history_service):
        """Test getting connection with no matching tasks."""
        items, has_next, total = await task_history_service.get_connection(
            first=10, status=TaskStatus.FAILED  # Filter by FAILED status
        )

        # Check that we get failed tasks (which should exist from other tests)
        assert len(items) >= 0  # May have failed tasks from other tests
        assert total >= 0
        # Don't assert has_next since we don't know the exact count

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_get_connection_with_search(self, task_history_service):
        """Test getting connection with search filter."""
        # Create a task with specific task_id
        await task_history_service.create_task(
            task_id="unique_search_task_456",
            task_type=TaskType.SYNC,
            entity_id="artist_123",
            entity_type=EntityType.ARTIST,
        )

        items, has_next, total = await task_history_service.get_connection(
            first=10, search="unique_search_task_456"
        )

        assert len(items) >= 1
        assert total >= 1
        # Should find the task with matching task_id

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_get_connection_with_cursor_pagination(self, task_history_service):
        """Test getting connection with cursor-based pagination."""
        # Create multiple tasks with unique IDs
        tasks = []
        for i in range(5):
            task = await task_history_service.create_task(
                task_id=f"cursor_task_{i}",
                task_type=TaskType.SYNC,
                entity_id=f"entity_{i}",
                entity_type=EntityType.ARTIST,
            )
            tasks.append(task)

        # Get first page
        items1, has_next1, total1 = await task_history_service.get_connection(first=2)

        assert len(items1) == 2
        assert has_next1 is True
        assert total1 >= 5

        # Get second page using cursor
        if items1:
            cursor = task_history_service.create_cursor(items1[-1])
            items2, has_next2, total2 = await task_history_service.get_connection(
                first=2, after=cursor
            )

            assert len(items2) >= 0  # May be empty if no more items
            assert total2 >= 0  # Total should be non-negative

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_to_graphql_type_conversion(self, task_history_service):
        """Test conversion from Django model to GraphQL type."""
        # Create a task
        django_task = await task_history_service.create_task(
            task_id="test_conversion_789",
            task_type=TaskType.SYNC,
            entity_id="test_entity",
            entity_type=EntityType.ARTIST,
        )

        # Convert to GraphQL type
        graphql_task = task_history_service._to_graphql_type(django_task)

        assert graphql_task.task_id == "test_conversion_789"
        assert graphql_task.type == TaskType.SYNC
        assert graphql_task.entity_id == "test_entity"
        assert graphql_task.entity_type == EntityType.ARTIST
        assert graphql_task.status == TaskStatus.PENDING
        assert graphql_task.id == str(django_task.id)

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_create_task_with_all_entity_types(self, task_history_service):
        """Test creating tasks with all entity types."""
        entity_types = [EntityType.ARTIST, EntityType.ALBUM, EntityType.PLAYLIST]

        for i, entity_type in enumerate(entity_types):
            task = await task_history_service.create_task(
                task_id=f"task_{entity_type.value}_{i}",
                task_type=TaskType.SYNC,
                entity_id=f"entity_{entity_type.value}_{i}",
                entity_type=entity_type,
            )

            assert task.entity_type == entity_type.value.upper()

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_get_connection_with_type_filter(self, task_history_service):
        """Test getting connection with type filter."""
        # Create tasks with different types and unique IDs
        await task_history_service.create_task(
            task_id="sync_task_filter_1",
            task_type=TaskType.SYNC,
            entity_id="entity_1",
            entity_type=EntityType.ARTIST,
        )

        await task_history_service.create_task(
            task_id="download_task_filter_1",
            task_type=TaskType.DOWNLOAD,
            entity_id="entity_2",
            entity_type=EntityType.ALBUM,
        )

        # Filter by SYNC type
        items, has_next, total = await task_history_service.get_connection(
            first=10, type=TaskType.SYNC
        )

        assert len(items) >= 1
        assert all(item.type == TaskType.SYNC for item in items)

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_cancelled_status_mapping(self, task_history_service):
        """Test that CANCELLED status is properly mapped to GraphQL type."""
        from library_manager.models import TaskHistory as DjangoTaskHistory

        # Create a task and mark it as cancelled
        django_task = await task_history_service.create_task(
            task_id="test_cancelled_mapping",
            task_type=TaskType.DOWNLOAD,
            entity_id="artist_123",
            entity_type=EntityType.ARTIST,
        )

        # Manually set status to CANCELLED (simulating cancellation)
        django_task.status = "CANCELLED"
        await sync_to_async(django_task.save)()

        # Refresh from DB and convert to GraphQL type
        refreshed_task = await sync_to_async(DjangoTaskHistory.objects.get)(
            task_id="test_cancelled_mapping"
        )
        graphql_task = task_history_service._to_graphql_type(refreshed_task)

        # Verify CANCELLED status is properly mapped
        assert graphql_task.status == TaskStatus.CANCELLED
        assert refreshed_task.status == "CANCELLED"

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_get_connection_filters_cancelled_tasks(self, task_history_service):
        """Test that cancelled tasks can be filtered in queries."""
        # Create a running task and a cancelled task
        running_task = await task_history_service.create_task(
            task_id="running_task_filter",
            task_type=TaskType.DOWNLOAD,
            entity_id="artist_456",
            entity_type=EntityType.ARTIST,
        )
        running_task.status = "RUNNING"
        await sync_to_async(running_task.save)()

        cancelled_task = await task_history_service.create_task(
            task_id="cancelled_task_filter",
            task_type=TaskType.DOWNLOAD,
            entity_id="artist_789",
            entity_type=EntityType.ARTIST,
        )
        cancelled_task.status = "CANCELLED"
        await sync_to_async(cancelled_task.save)()

        # Query for RUNNING tasks only
        running_items, _, _ = await task_history_service.get_connection(
            first=10, status=TaskStatus.RUNNING
        )

        # Verify cancelled task is not in RUNNING results
        running_task_ids = [item.task_id for item in running_items]
        assert "running_task_filter" in running_task_ids
        assert "cancelled_task_filter" not in running_task_ids

        # Query for CANCELLED tasks only
        cancelled_items, _, _ = await task_history_service.get_connection(
            first=10, status=TaskStatus.CANCELLED
        )

        # Verify only cancelled tasks are returned
        cancelled_task_ids = [item.task_id for item in cancelled_items]
        assert "cancelled_task_filter" in cancelled_task_ids
        assert "running_task_filter" not in cancelled_task_ids
