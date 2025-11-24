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
            patch("src.services.task_management.TaskResult") as mock_task_result,
            patch(
                "src.services.task_management.TaskManagementService.get_task_count_by_name"
            ) as mock_task_count,
        ):

            # Mock database query to return count of 3 pending tasks
            mock_queryset = Mock()
            mock_queryset.count.return_value = 3
            mock_task_result.objects.filter.return_value = mock_queryset

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
            patch("src.services.task_management.TaskResult") as mock_task_result,
            patch(
                "src.services.task_management.TaskManagementService.get_task_count_by_name"
            ) as mock_task_count,
        ):

            # Mock database query to return count of 0
            mock_queryset = Mock()
            mock_queryset.count.return_value = 0
            mock_task_result.objects.filter.return_value = mock_queryset

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

        with patch("src.services.task_management.TaskResult") as mock_task_result:
            # Mock database update to return 2 updated rows
            mock_queryset = Mock()
            mock_queryset.update.return_value = 2
            mock_task_result.objects.filter.return_value = mock_queryset

            result = await schema.execute(mutation)

            assert result.errors is None
            assert result.data is not None

            mutation_result = result.data["cancelAllPendingTasks"]
            assert mutation_result["success"] is True
            assert (
                "Successfully cancelled 2 pending tasks" in mutation_result["message"]
            )

            # Verify update was called
            mock_queryset.update.assert_called_once_with(status="REVOKED")

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

        with patch("src.services.task_management.TaskResult") as mock_task_result:
            # Mock database update to return 0 updated rows
            mock_queryset = Mock()
            mock_queryset.update.return_value = 0
            mock_task_result.objects.filter.return_value = mock_queryset

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

        with patch("src.services.task_management.TaskResult") as mock_task_result:
            # Mock database update to return 2 updated rows
            mock_queryset = Mock()
            mock_queryset.update.return_value = 2
            mock_task_result.objects.filter.return_value = mock_queryset

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

        with patch("src.services.task_management.TaskResult") as mock_task_result:
            # Mock database update to return 0 updated rows
            mock_queryset = Mock()
            mock_queryset.update.return_value = 0
            mock_task_result.objects.filter.return_value = mock_queryset

            result = await schema.execute(mutation, variable_values=variables)

            assert result.errors is None
            assert result.data is not None

            mutation_result = result.data["cancelTasksByName"]
            assert mutation_result["success"] is True
            assert "Successfully cancelled 0 tasks" in mutation_result["message"]

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_cancel_tasks_by_name_mutation_multiple_tasks(self):
        """Test cancel tasks by name mutation with multiple matching tasks."""
        mutation = """
        mutation CancelTasksByName($taskName: String!) {
            cancelTasksByName(taskName: $taskName) {
                success
                message
            }
        }
        """

        variables = {"taskName": "download_playlist"}

        with patch("src.services.task_management.TaskResult") as mock_task_result:
            # Mock database update to return 5 updated rows
            mock_queryset = Mock()
            mock_queryset.update.return_value = 5
            mock_task_result.objects.filter.return_value = mock_queryset

            result = await schema.execute(mutation, variable_values=variables)

            assert result.errors is None
            assert result.data is not None

            mutation_result = result.data["cancelTasksByName"]
            assert mutation_result["success"] is True
            assert "Successfully cancelled 5 tasks" in mutation_result["message"]

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_task_history_query_with_fixed_cursor(self):
        """Test task history query with the fixed cursor implementation."""
        # Create some test task history records (let factory generate unique task_ids)
        await sync_to_async(TaskHistoryFactory)()
        await sync_to_async(TaskHistoryFactory)()

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
        """Test queue status query handles database exceptions gracefully."""
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

        with patch("src.services.task_management.TaskResult") as mock_task_result:
            mock_task_result.objects.filter.side_effect = Exception(
                "Database connection error"
            )

            result = await schema.execute(query)

            # GraphQL should propagate the exception as an error
            assert result.errors is not None
            assert len(result.errors) == 1
            assert "Database connection error" in str(result.errors[0])
            assert result.data is None

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_cancel_all_pending_tasks_mutation_exception_handling(self):
        """Test cancel all pending tasks mutation handles database exceptions gracefully."""
        mutation = """
        mutation {
            cancelAllPendingTasks {
                success
                message
            }
        }
        """

        with patch("src.services.task_management.TaskResult") as mock_task_result:
            mock_task_result.objects.filter.side_effect = Exception(
                "Database connection error"
            )

            result = await schema.execute(mutation)

            assert result.errors is None
            assert result.data is not None

            mutation_result = result.data["cancelAllPendingTasks"]
            assert mutation_result["success"] is False
            assert "Failed to cancel tasks" in mutation_result["message"]
