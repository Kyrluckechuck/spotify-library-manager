"""Unit tests for task management service."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from huey.api import Task

from src.services.task_management import MutationResult, TaskManagementService


@pytest.fixture
def task_management_service():
    return TaskManagementService()


@pytest.fixture
def mock_huey():
    """Mock Huey instance for testing."""
    return Mock()


@pytest.fixture
def mock_pending_task():
    """Mock a pending Huey task."""
    task = Mock(spec=Task)
    task.id = "task_123"
    task.name = "test_task"
    task.args = ["arg1", "arg2"]
    task.kwargs = {"key1": "value1"}
    task.priority = 1
    task.created_at = datetime.now()
    return task


class TestTaskManagementService:
    """Test TaskManagementService functionality."""

    def test_task_management_service_initialization(self, task_management_service):
        """Test TaskManagementService can be initialized."""
        assert task_management_service is not None
        assert hasattr(task_management_service, "get_pending_tasks")
        assert hasattr(task_management_service, "get_task_count_by_name")
        assert hasattr(task_management_service, "cancel_all_pending_tasks")
        assert hasattr(task_management_service, "cancel_tasks_by_name")
        assert hasattr(task_management_service, "get_queue_status")

    @patch("src.services.task_management.HUEY")
    def test_get_pending_tasks_success(
        self, mock_huey, task_management_service, mock_pending_task
    ):
        """Test getting pending tasks successfully."""
        mock_huey.pending.return_value = [mock_pending_task]

        result = task_management_service.get_pending_tasks()

        assert len(result) == 1
        assert result[0]["id"] == "task_123"
        assert result[0]["name"] == "test_task"
        assert result[0]["args"] == ["arg1", "arg2"]
        assert result[0]["kwargs"] == {"key1": "value1"}
        assert result[0]["priority"] == 1
        assert result[0]["created_at"] is not None

    @patch("src.services.task_management.HUEY")
    def test_get_pending_tasks_empty(self, mock_huey, task_management_service):
        """Test getting pending tasks when queue is empty."""
        mock_huey.pending.return_value = []

        result = task_management_service.get_pending_tasks()

        assert result == []

    @patch("src.services.task_management.HUEY")
    def test_get_pending_tasks_exception(self, mock_huey, task_management_service):
        """Test getting pending tasks when Huey raises an exception."""
        mock_huey.pending.side_effect = Exception("Huey error")

        # The actual implementation doesn't handle exceptions, so this should raise
        with pytest.raises(Exception, match="Huey error"):
            task_management_service.get_pending_tasks()

    @patch("src.services.task_management.HUEY")
    @pytest.mark.asyncio
    async def test_get_task_count_by_name(
        self, mock_huey, task_management_service, mock_pending_task
    ):
        """Test getting task count by name."""
        # Mock the TaskHistory model and its query
        with patch("library_manager.models.TaskHistory") as mock_task_history:
            # Mock the values() call to return task types
            mock_values = Mock()
            mock_values.__iter__ = Mock(
                return_value=iter(
                    [
                        {"type": "test_task"},
                        {"type": "test_task"},
                        {"type": "other_task"},
                    ]
                )
            )
            mock_task_history.objects.values.return_value = mock_values

            result = await task_management_service.get_task_count_by_name()

            assert result["test_task"] == 2
            assert result["other_task"] == 1

    @patch("src.services.task_management.HUEY")
    @pytest.mark.asyncio
    async def test_get_task_count_by_name_not_found(
        self, mock_huey, task_management_service
    ):
        """Test getting task count for non-existent task name."""
        with patch("library_manager.models.TaskHistory") as mock_task_history:
            mock_values = Mock()
            mock_values.__iter__ = Mock(return_value=iter([]))
            mock_task_history.objects.values.return_value = mock_values

            result = await task_management_service.get_task_count_by_name()

            assert result == {}

    @patch("src.services.task_management.HUEY")
    @pytest.mark.asyncio
    async def test_cancel_all_pending_tasks_success(
        self, mock_huey, task_management_service, mock_pending_task
    ):
        """Test cancelling all pending tasks successfully."""
        mock_huey.pending.return_value = [mock_pending_task]
        mock_huey.revoke_by_id.return_value = True

        result = await task_management_service.cancel_all_pending_tasks()

        assert isinstance(result, MutationResult)
        assert result.success is True
        assert "Successfully cancelled 1 pending tasks" in result.message
        mock_huey.revoke_by_id.assert_called_once_with("task_123")

    @patch("src.services.task_management.HUEY")
    @pytest.mark.asyncio
    async def test_cancel_all_pending_tasks_empty_queue(
        self, mock_huey, task_management_service
    ):
        """Test cancelling all pending tasks when queue is empty."""
        mock_huey.pending.return_value = []

        result = await task_management_service.cancel_all_pending_tasks()

        assert isinstance(result, MutationResult)
        assert result.success is True
        assert "Successfully cancelled 0 pending tasks" in result.message

    @patch("src.services.task_management.HUEY")
    @pytest.mark.asyncio
    async def test_cancel_all_pending_tasks_partial_failure(
        self, mock_huey, task_management_service
    ):
        """Test cancelling all pending tasks with some failures."""
        task1 = Mock(spec=Task)
        task1.id = "task_1"
        task2 = Mock(spec=Task)
        task2.id = "task_2"

        mock_huey.pending.return_value = [task1, task2]
        mock_huey.revoke_by_id.side_effect = [True, Exception("Revoke failed")]

        result = await task_management_service.cancel_all_pending_tasks()

        assert isinstance(result, MutationResult)
        assert result.success is True
        assert "Successfully cancelled 1 pending tasks" in result.message

    @patch("src.services.task_management.HUEY")
    @pytest.mark.asyncio
    async def test_cancel_all_pending_tasks_huey_exception(
        self, mock_huey, task_management_service
    ):
        """Test cancelling all pending tasks when Huey raises an exception."""
        mock_huey.pending.side_effect = Exception("Huey error")

        result = await task_management_service.cancel_all_pending_tasks()

        assert isinstance(result, MutationResult)
        assert result.success is False
        assert "Failed to cancel tasks" in result.message

    @patch("src.services.task_management.HUEY")
    @pytest.mark.asyncio
    async def test_cancel_tasks_by_name_success(
        self, mock_huey, task_management_service
    ):
        """Test cancelling tasks by name successfully."""
        task1 = Mock(spec=Task)
        task1.id = "task_1"
        # Make the string representation include the task name for the service's string search
        task1.__str__ = Mock(return_value="test_task")
        task2 = Mock(spec=Task)
        task2.id = "task_2"
        task2.__str__ = Mock(return_value="test_task")
        task3 = Mock(spec=Task)
        task3.id = "task_3"
        task3.__str__ = Mock(return_value="other_task")

        mock_huey.pending.return_value = [task1, task2, task3]
        mock_huey.revoke_by_id.return_value = True

        result = await task_management_service.cancel_tasks_by_name("test_task")

        assert isinstance(result, MutationResult)
        assert result.success is True
        assert "Successfully cancelled 2 tasks" in result.message
        assert mock_huey.revoke_by_id.call_count == 2

    @patch("src.services.task_management.HUEY")
    @pytest.mark.asyncio
    async def test_cancel_tasks_by_name_not_found(
        self, mock_huey, task_management_service
    ):
        """Test cancelling tasks by name when no matching tasks exist."""
        mock_huey.pending.return_value = []

        result = await task_management_service.cancel_tasks_by_name("non_existent_task")

        assert isinstance(result, MutationResult)
        assert result.success is True
        assert "Successfully cancelled 0 tasks" in result.message

    @patch("src.services.task_management.HUEY")
    @pytest.mark.asyncio
    async def test_cancel_tasks_by_name_partial_failure(
        self, mock_huey, task_management_service
    ):
        """Test cancelling tasks by name with some failures."""
        task1 = Mock(spec=Task)
        task1.id = "task_1"
        task1.__str__ = Mock(return_value="test_task")
        task2 = Mock(spec=Task)
        task2.id = "task_2"
        task2.__str__ = Mock(return_value="test_task")

        mock_huey.pending.return_value = [task1, task2]
        mock_huey.revoke_by_id.side_effect = [True, Exception("Revoke failed")]

        result = await task_management_service.cancel_tasks_by_name("test_task")

        assert isinstance(result, MutationResult)
        assert result.success is True
        assert "Successfully cancelled 1 tasks" in result.message

    @patch("src.services.task_management.HUEY")
    @pytest.mark.asyncio
    async def test_cancel_running_tasks_by_name_success(
        self, mock_huey, task_management_service
    ):
        """Test cancelling running tasks by name successfully."""
        with patch("library_manager.models.TaskHistory") as mock_task_history:
            # Mock running tasks
            mock_task1 = Mock()
            mock_task1.task_id = "task_1"
            mock_task1.status = "RUNNING"
            mock_task1.save.return_value = None

            mock_task2 = Mock()
            mock_task2.task_id = "task_2"
            mock_task2.status = "RUNNING"
            mock_task2.save.return_value = None

            mock_task_history.objects.filter.return_value = [mock_task1, mock_task2]

            result = await task_management_service.cancel_running_tasks_by_name(
                "download_playlist"
            )

            assert isinstance(result, MutationResult)
            assert result.success is True
            assert "Successfully cancelled 2 running tasks" in result.message

    @patch("src.services.task_management.HUEY")
    @pytest.mark.asyncio
    async def test_cancel_all_tasks_success(self, mock_huey, task_management_service):
        """Test cancelling all tasks (pending and running) successfully."""
        # Mock pending tasks
        task1 = Mock(spec=Task)
        task1.id = "task_1"
        task1.name = "test_task"
        mock_huey.pending.return_value = [task1]
        mock_huey.revoke_by_id.return_value = True

        # Mock running tasks
        with patch("library_manager.models.TaskHistory") as mock_task_history:
            mock_running_task = Mock()
            mock_running_task.task_id = "task_2"
            mock_running_task.status = "RUNNING"
            mock_running_task.save.return_value = None

            mock_task_history.objects.filter.return_value = [mock_running_task]

            result = await task_management_service.cancel_all_tasks()

            assert isinstance(result, MutationResult)
            assert result.success is True
            assert "Successfully cancelled 2 total tasks" in result.message

    @patch("src.services.task_management.HUEY")
    @pytest.mark.asyncio
    async def test_get_queue_status_success(self, mock_huey, task_management_service):
        """Test getting queue status successfully."""
        task1 = Mock(spec=Task)
        task1.name = "task_a"
        task2 = Mock(spec=Task)
        task2.name = "task_a"
        task3 = Mock(spec=Task)
        task3.name = "task_b"

        mock_huey.pending.return_value = [task1, task2, task3]
        mock_huey.storage.queue_size.return_value = 3

        # Mock the async get_task_count_by_name method
        with patch.object(
            task_management_service,
            "get_task_count_by_name",
            return_value={"task_a": 2, "task_b": 1},
        ):
            result = await task_management_service.get_queue_status()

        assert result["total_pending_tasks"] == 3
        assert result["queue_size"] == 3
        assert result["task_counts"]["task_a"] == 2
        assert result["task_counts"]["task_b"] == 1

    @patch("src.services.task_management.HUEY")
    @pytest.mark.asyncio
    async def test_get_queue_status_empty(self, mock_huey, task_management_service):
        """Test getting queue status when queue is empty."""
        mock_huey.pending.return_value = []
        mock_huey.storage.queue_size.return_value = 0

        # Mock the async get_task_count_by_name method
        with patch.object(
            task_management_service, "get_task_count_by_name", return_value={}
        ):
            result = await task_management_service.get_queue_status()

        assert result["total_pending_tasks"] == 0
        assert result["queue_size"] == 0
        assert result["task_counts"] == {}

    @patch("src.services.task_management.HUEY")
    @pytest.mark.asyncio
    async def test_get_queue_status_exception(self, mock_huey, task_management_service):
        """Test getting queue status when Huey raises an exception."""
        mock_huey.pending.side_effect = Exception("Huey error")

        # The actual implementation doesn't handle exceptions, so this should raise
        with pytest.raises(Exception, match="Huey error"):
            await task_management_service.get_queue_status()

    def test_mutation_result_creation(self):
        """Test MutationResult creation for task management."""
        success_result = MutationResult(success=True, message="Success")
        assert success_result.success is True
        assert success_result.message == "Success"

        failure_result = MutationResult(success=False, message="Failed")
        assert failure_result.success is False
        assert failure_result.message == "Failed"
