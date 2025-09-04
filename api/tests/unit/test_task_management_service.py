"""Unit tests for task management service."""

from unittest.mock import Mock, patch

import pytest

from src.services.task_management import MutationResult, TaskManagementService


@pytest.fixture
def task_management_service():
    return TaskManagementService()


@pytest.fixture
def mock_celery_app():
    """Mock Celery app instance for testing."""
    return Mock()


@pytest.fixture
def mock_celery_task():
    """Mock a Celery task result."""
    return {
        "id": "task_123",
        "name": "test_task",
        "args": ["arg1", "arg2"],
        "kwargs": {"key1": "value1"},
    }


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

    @patch("src.services.task_management.current_app")
    def test_get_pending_tasks_success(
        self, mock_celery_app, task_management_service, mock_celery_task
    ):
        """Test getting pending tasks successfully."""
        mock_inspect = Mock()
        mock_inspect.active.return_value = {"worker1": [mock_celery_task]}
        mock_celery_app.control.inspect.return_value = mock_inspect

        result = task_management_service.get_pending_tasks()

        assert len(result) == 1
        assert result[0]["id"] == "task_123"
        assert result[0]["name"] == "test_task"
        assert result[0]["args"] == ["arg1", "arg2"]
        assert result[0]["kwargs"] == {"key1": "value1"}

    @patch("src.services.task_management.current_app")
    def test_get_pending_tasks_empty(self, mock_celery_app, task_management_service):
        """Test getting pending tasks when queue is empty."""
        mock_inspect = Mock()
        mock_inspect.active.return_value = {}
        mock_celery_app.control.inspect.return_value = mock_inspect

        result = task_management_service.get_pending_tasks()

        assert result == []

    @patch("src.services.task_management.current_app")
    def test_get_pending_tasks_exception(
        self, mock_celery_app, task_management_service
    ):
        """Test getting pending tasks when Celery raises an exception."""
        mock_celery_app.control.inspect.side_effect = Exception("Celery error")

        # The actual implementation doesn't handle exceptions, so this should raise
        with pytest.raises(Exception, match="Celery error"):
            task_management_service.get_pending_tasks()

    @pytest.mark.asyncio
    async def test_get_task_count_by_name(self, task_management_service):
        """Test getting task count by name."""
        # Mock the TaskResult model and its query
        with patch("src.services.task_management.TaskResult") as mock_task_result:
            # Mock the filter and values chain
            mock_queryset = Mock()
            mock_values = Mock()
            mock_values.__iter__ = Mock(
                return_value=iter(
                    [
                        {"task_name": "test_task"},
                        {"task_name": "test_task"},
                        {"task_name": "other_task"},
                    ]
                )
            )
            mock_queryset.values.return_value = mock_values
            mock_task_result.objects.filter.return_value = mock_queryset

            result = await task_management_service.get_task_count_by_name()

            assert result["test_task"] == 2
            assert result["other_task"] == 1

    @pytest.mark.asyncio
    async def test_get_task_count_by_name_not_found(self, task_management_service):
        """Test getting task count for non-existent task name."""
        with patch("src.services.task_management.TaskResult") as mock_task_result:
            mock_queryset = Mock()
            mock_values = Mock()
            mock_values.__iter__ = Mock(return_value=iter([]))
            mock_queryset.values.return_value = mock_values
            mock_task_result.objects.filter.return_value = mock_queryset

            result = await task_management_service.get_task_count_by_name()

            assert result == {}

    @patch("src.services.task_management.current_app")
    @pytest.mark.asyncio
    async def test_cancel_all_pending_tasks_success(
        self, mock_celery_app, task_management_service, mock_celery_task
    ):
        """Test cancelling all pending tasks successfully."""
        mock_inspect = Mock()
        mock_inspect.active.return_value = {"worker1": [mock_celery_task]}
        mock_celery_app.control.inspect.return_value = mock_inspect
        mock_celery_app.control.revoke.return_value = None

        result = await task_management_service.cancel_all_pending_tasks()

        assert isinstance(result, MutationResult)
        assert result.success is True
        assert "Successfully cancelled 1 pending tasks" in result.message
        mock_celery_app.control.revoke.assert_called_once_with(
            "task_123", terminate=True
        )

    @patch("src.services.task_management.current_app")
    @pytest.mark.asyncio
    async def test_cancel_all_pending_tasks_empty_queue(
        self, mock_celery_app, task_management_service
    ):
        """Test cancelling all pending tasks when queue is empty."""
        mock_inspect = Mock()
        mock_inspect.active.return_value = {}
        mock_celery_app.control.inspect.return_value = mock_inspect

        result = await task_management_service.cancel_all_pending_tasks()

        assert isinstance(result, MutationResult)
        assert result.success is True
        assert "Successfully cancelled 0 pending tasks" in result.message

    @patch("src.services.task_management.current_app")
    @pytest.mark.asyncio
    async def test_cancel_all_pending_tasks_partial_failure(
        self, mock_celery_app, task_management_service
    ):
        """Test cancelling all pending tasks with some failures."""
        task1 = {"id": "task_1", "name": "test_task"}
        task2 = {"id": "task_2", "name": "test_task"}

        mock_inspect = Mock()
        mock_inspect.active.return_value = {"worker1": [task1, task2]}
        mock_celery_app.control.inspect.return_value = mock_inspect
        mock_celery_app.control.revoke.side_effect = [None, Exception("Revoke failed")]

        result = await task_management_service.cancel_all_pending_tasks()

        assert isinstance(result, MutationResult)
        assert result.success is True
        assert "Successfully cancelled 1 pending tasks" in result.message

    @patch("src.services.task_management.current_app")
    @pytest.mark.asyncio
    async def test_cancel_all_pending_tasks_celery_exception(
        self, mock_celery_app, task_management_service
    ):
        """Test cancelling all pending tasks when Celery raises an exception."""
        mock_celery_app.control.inspect.side_effect = Exception("Celery error")

        result = await task_management_service.cancel_all_pending_tasks()

        assert isinstance(result, MutationResult)
        assert result.success is False
        assert "Failed to cancel tasks" in result.message

    @patch("src.services.task_management.current_app")
    @pytest.mark.asyncio
    async def test_cancel_tasks_by_name_success(
        self, mock_celery_app, task_management_service
    ):
        """Test cancelling tasks by name successfully."""
        task1 = {"id": "task_1", "name": "test_task"}
        task2 = {"id": "task_2", "name": "test_task"}
        task3 = {"id": "task_3", "name": "other_task"}

        mock_inspect = Mock()
        mock_inspect.active.return_value = {"worker1": [task1, task2, task3]}
        mock_celery_app.control.inspect.return_value = mock_inspect
        mock_celery_app.control.revoke.return_value = None

        result = await task_management_service.cancel_tasks_by_name("test_task")

        assert isinstance(result, MutationResult)
        assert result.success is True
        assert "Successfully cancelled 2 tasks" in result.message
        assert mock_celery_app.control.revoke.call_count == 2

    @patch("src.services.task_management.current_app")
    @pytest.mark.asyncio
    async def test_cancel_tasks_by_name_not_found(
        self, mock_celery_app, task_management_service
    ):
        """Test cancelling tasks by name when no matching tasks exist."""
        mock_inspect = Mock()
        mock_inspect.active.return_value = {}
        mock_celery_app.control.inspect.return_value = mock_inspect

        result = await task_management_service.cancel_tasks_by_name("non_existent_task")

        assert isinstance(result, MutationResult)
        assert result.success is True
        assert "Successfully cancelled 0 tasks" in result.message

    @patch("src.services.task_management.current_app")
    @pytest.mark.asyncio
    async def test_cancel_tasks_by_name_partial_failure(
        self, mock_celery_app, task_management_service
    ):
        """Test cancelling tasks by name with some failures."""
        task1 = {"id": "task_1", "name": "test_task"}
        task2 = {"id": "task_2", "name": "test_task"}

        mock_inspect = Mock()
        mock_inspect.active.return_value = {"worker1": [task1, task2]}
        mock_celery_app.control.inspect.return_value = mock_inspect
        mock_celery_app.control.revoke.side_effect = [None, Exception("Revoke failed")]

        result = await task_management_service.cancel_tasks_by_name("test_task")

        assert isinstance(result, MutationResult)
        assert result.success is True
        assert "Successfully cancelled 1 tasks" in result.message

    @pytest.mark.asyncio
    async def test_cancel_running_tasks_by_name_success(self, task_management_service):
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

    @patch("src.services.task_management.current_app")
    @pytest.mark.asyncio
    async def test_cancel_all_tasks_success(
        self, mock_celery_app, task_management_service
    ):
        """Test cancelling all tasks (pending and running) successfully."""
        # Mock pending tasks
        task1 = {"id": "task_1", "name": "test_task"}
        mock_inspect = Mock()
        mock_inspect.active.return_value = {"worker1": [task1]}
        mock_celery_app.control.inspect.return_value = mock_inspect
        mock_celery_app.control.revoke.return_value = None

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

    @patch("src.services.task_management.current_app")
    @pytest.mark.asyncio
    async def test_get_queue_status_success(
        self, mock_celery_app, task_management_service
    ):
        """Test getting queue status successfully."""
        task1 = {"id": "task_1", "name": "task_a"}
        task2 = {"id": "task_2", "name": "task_a"}
        task3 = {"id": "task_3", "name": "task_b"}

        mock_inspect = Mock()
        mock_inspect.active.return_value = {"worker1": [task1, task2, task3]}
        mock_celery_app.control.inspect.return_value = mock_inspect

        # Mock the async get_task_count_by_name method
        with patch.object(
            task_management_service,
            "get_task_count_by_name",
            return_value={"task_a": 2, "task_b": 1},
        ):
            result = await task_management_service.get_queue_status()

        assert result["total_pending_tasks"] == 3
        assert result["task_counts"]["task_a"] == 2
        assert result["task_counts"]["task_b"] == 1

    @patch("src.services.task_management.current_app")
    @pytest.mark.asyncio
    async def test_get_queue_status_empty(
        self, mock_celery_app, task_management_service
    ):
        """Test getting queue status when queue is empty."""
        mock_inspect = Mock()
        mock_inspect.active.return_value = {}
        mock_celery_app.control.inspect.return_value = mock_inspect

        # Mock the async get_task_count_by_name method
        with patch.object(
            task_management_service, "get_task_count_by_name", return_value={}
        ):
            result = await task_management_service.get_queue_status()

        assert result["total_pending_tasks"] == 0
        assert result["task_counts"] == {}

    @patch("src.services.task_management.current_app")
    @pytest.mark.asyncio
    async def test_get_queue_status_exception(
        self, mock_celery_app, task_management_service
    ):
        """Test getting queue status when Celery raises an exception."""
        mock_celery_app.control.inspect.side_effect = Exception("Celery error")

        # The actual implementation doesn't handle exceptions, so this should raise
        with pytest.raises(Exception, match="Celery error"):
            await task_management_service.get_queue_status()

    def test_mutation_result_creation(self):
        """Test MutationResult creation for task management."""
        success_result = MutationResult(success=True, message="Success")
        assert success_result.success is True
        assert success_result.message == "Success"

        failure_result = MutationResult(success=False, message="Failed")
        assert failure_result.success is False
        assert failure_result.message == "Failed"
