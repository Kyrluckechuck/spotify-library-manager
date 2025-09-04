"""Unit tests for task management GraphQL schema."""

from unittest.mock import Mock, patch

import pytest
from asgiref.sync import sync_to_async
from tests.factories import TaskHistoryFactory

from src.schema import schema


class TestTaskManagementGraphQL:
    """Test task management GraphQL queries and mutations."""

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_queue_status_query_success(self):
        """Test queue status query returns correct data."""
        query = """
        query {
            queueStatus {
                totalPendingTasks
                taskCounts {
                    taskName
                    count
                }
            }
        }
        """

        with (
            patch("src.services.task_management.current_app") as mock_celery_app,
            patch(
                "src.services.task_management.TaskManagementService.get_task_count_by_name"
            ) as mock_task_count,
        ):

            # Mock Celery to return some active tasks
            mock_inspect = Mock()
            mock_inspect.active.return_value = {
                "worker1": [
                    {"id": "task_1", "name": "download_playlist"},
                    {"id": "task_2", "name": "download_playlist"},
                    {"id": "task_3", "name": "sync_playlist"},
                ]
            }
            mock_celery_app.control.inspect.return_value = mock_inspect

            # Mock the task count method to return expected data
            mock_task_count.return_value = {
                "download_playlist": 2,
                "sync_playlist": 1,
            }

            result = await schema.execute(query)

            assert result.errors is None
            assert result.data is not None

            queue_status = result.data["queueStatus"]
            assert queue_status["totalPendingTasks"] == 3

            # Check task counts
            task_counts = queue_status["taskCounts"]
            assert len(task_counts) == 2

            # Find the download_playlist count
            download_count = next(
                (
                    tc["count"]
                    for tc in task_counts
                    if tc["taskName"] == "download_playlist"
                ),
                None,
            )
            assert download_count == 2

            # Find the sync_playlist count
            sync_count = next(
                (
                    tc["count"]
                    for tc in task_counts
                    if tc["taskName"] == "sync_playlist"
                ),
                None,
            )
            assert sync_count == 1

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_queue_status_query_empty(self):
        """Test queue status query when queue is empty."""
        query = """
        query {
            queueStatus {
                totalPendingTasks
                taskCounts {
                    taskName
                    count
                }
            }
        }
        """

        with (
            patch("src.services.task_management.current_app") as mock_celery_app,
            patch(
                "src.services.task_management.TaskManagementService.get_task_count_by_name"
            ) as mock_task_count,
        ):

            mock_inspect = Mock()
            mock_inspect.active.return_value = {}
            mock_celery_app.control.inspect.return_value = mock_inspect

            # Mock empty task counts
            mock_task_count.return_value = {}

            result = await schema.execute(query)

            assert result.errors is None
            assert result.data is not None

            queue_status = result.data["queueStatus"]
            assert queue_status["totalPendingTasks"] == 0
            assert queue_status["taskCounts"] == []

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_cancel_all_pending_tasks_mutation_success(self):
        """Test cancel all pending tasks mutation."""
        mutation = """
        mutation {
            cancelAllPendingTasks {
                success
                message
            }
        }
        """

        with patch("src.services.task_management.current_app") as mock_celery_app:
            # Mock some active tasks
            mock_inspect = Mock()
            mock_inspect.active.return_value = {
                "worker1": [
                    {"id": "task_1", "name": "download_playlist"},
                    {"id": "task_2", "name": "sync_playlist"},
                ]
            }
            mock_celery_app.control.inspect.return_value = mock_inspect
            mock_celery_app.control.revoke.return_value = None

            result = await schema.execute(mutation)

            assert result.errors is None
            assert result.data is not None

            mutation_result = result.data["cancelAllPendingTasks"]
            assert mutation_result["success"] is True
            assert (
                "Successfully cancelled 2 pending tasks" in mutation_result["message"]
            )

            # Verify revoke was called
            mock_celery_app.control.revoke.assert_called()

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_cancel_all_pending_tasks_mutation_empty(self):
        """Test cancel all pending tasks mutation when queue is empty."""
        mutation = """
        mutation {
            cancelAllPendingTasks {
                success
                message
            }
        }
        """

        with patch("src.services.task_management.current_app") as mock_celery_app:
            mock_inspect = Mock()
            mock_inspect.active.return_value = {}
            mock_celery_app.control.inspect.return_value = mock_inspect

            result = await schema.execute(mutation)

            assert result.errors is None
            assert result.data is not None

            mutation_result = result.data["cancelAllPendingTasks"]
            assert mutation_result["success"] is True
            assert (
                "Successfully cancelled 0 pending tasks" in mutation_result["message"]
            )

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_cancel_tasks_by_name_mutation_success(self):
        """Test cancel tasks by name mutation."""
        mutation = """
        mutation CancelTasksByName($taskName: String!) {
            cancelTasksByName(taskName: $taskName) {
                success
                message
            }
        }
        """

        variables = {"taskName": "download_playlist"}

        with patch("src.services.task_management.current_app") as mock_celery_app:
            # Mock tasks with the specified name
            mock_inspect = Mock()
            mock_inspect.active.return_value = {
                "worker1": [
                    {"id": "task_1", "name": "download_playlist"},
                    {"id": "task_2", "name": "download_playlist"},
                    {"id": "task_3", "name": "sync_playlist"},
                ]
            }
            mock_celery_app.control.inspect.return_value = mock_inspect
            mock_celery_app.control.revoke.return_value = None

            result = await schema.execute(mutation, variable_values=variables)

            assert result.errors is None
            assert result.data is not None

            mutation_result = result.data["cancelTasksByName"]
            assert mutation_result["success"] is True
            assert "Successfully cancelled 2 tasks" in mutation_result["message"]

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_cancel_tasks_by_name_mutation_not_found(self):
        """Test cancel tasks by name mutation when no matching tasks exist."""
        mutation = """
        mutation CancelTasksByName($taskName: String!) {
            cancelTasksByName(taskName: $taskName) {
                success
                message
            }
        }
        """

        variables = {"taskName": "non_existent_task"}

        with patch("src.services.task_management.current_app") as mock_celery_app:
            mock_inspect = Mock()
            mock_inspect.active.return_value = {}
            mock_celery_app.control.inspect.return_value = mock_inspect

            result = await schema.execute(mutation, variable_values=variables)

            assert result.errors is None
            assert result.data is not None

            mutation_result = result.data["cancelTasksByName"]
            assert mutation_result["success"] is True
            assert "Successfully cancelled 0 tasks" in mutation_result["message"]

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_cancel_tasks_by_name_mutation_partial_failure(self):
        """Test cancel tasks by name mutation with partial failures."""
        mutation = """
        mutation CancelTasksByName($taskName: String!) {
            cancelTasksByName(taskName: $taskName) {
                success
                message
            }
        }
        """

        variables = {"taskName": "download_playlist"}

        with patch("src.services.task_management.current_app") as mock_celery_app:
            task1 = {"id": "task_1", "name": "download_playlist"}
            task2 = {"id": "task_2", "name": "download_playlist"}

            mock_inspect = Mock()
            mock_inspect.active.return_value = {"worker1": [task1, task2]}
            mock_celery_app.control.inspect.return_value = mock_inspect
            mock_celery_app.control.revoke.side_effect = [
                None,
                Exception("Revoke failed"),
            ]

            result = await schema.execute(mutation, variable_values=variables)

            assert result.errors is None
            assert result.data is not None

            mutation_result = result.data["cancelTasksByName"]
            assert mutation_result["success"] is True
            assert "Successfully cancelled 1 tasks" in mutation_result["message"]

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_task_history_query_with_fixed_cursor(self):
        """Test task history query with the fixed cursor implementation."""
        # Create some test task history records
        await sync_to_async(TaskHistoryFactory)(task_id="test_task_1")
        await sync_to_async(TaskHistoryFactory)(task_id="test_task_2")

        query = """
        query {
            taskHistory(first: 5) {
                totalCount
                edges {
                    node {
                        id
                        taskId
                        type
                        status
                    }
                    cursor
                }
            }
        }
        """

        result = await schema.execute(query)

        assert result.errors is None
        assert result.data is not None

        task_history = result.data["taskHistory"]
        assert task_history["totalCount"] >= 2

        edges = task_history["edges"]
        assert len(edges) >= 2

        # Verify each edge has proper structure
        for edge in edges:
            assert "node" in edge
            assert "cursor" in edge
            assert edge["cursor"] is not None
            assert edge["node"]["id"] is not None
            assert edge["node"]["taskId"] is not None

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_queue_status_query_exception_handling(self):
        """Test queue status query handles Celery exceptions gracefully."""
        query = """
        query {
            queueStatus {
                totalPendingTasks
                taskCounts {
                    taskName
                    count
                }
            }
        }
        """

        with patch("src.services.task_management.current_app") as mock_celery_app:
            mock_celery_app.control.inspect.side_effect = Exception(
                "Celery connection error"
            )

            result = await schema.execute(query)

            # GraphQL should propagate the exception as an error
            assert result.errors is not None
            assert len(result.errors) == 1
            assert "Celery connection error" in str(result.errors[0])
            assert result.data is None

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_cancel_all_pending_tasks_mutation_exception_handling(self):
        """Test cancel all pending tasks mutation handles Celery exceptions gracefully."""
        mutation = """
        mutation {
            cancelAllPendingTasks {
                success
                message
            }
        }
        """

        with patch("src.services.task_management.current_app") as mock_celery_app:
            mock_celery_app.control.inspect.side_effect = Exception(
                "Celery connection error"
            )

            result = await schema.execute(mutation)

            assert result.errors is None
            assert result.data is not None

            mutation_result = result.data["cancelAllPendingTasks"]
            assert mutation_result["success"] is False
            assert "Failed to cancel tasks" in mutation_result["message"]
