"""
Task management service for handling Celery task operations.
"""

from typing import Any, Dict

from django.utils import timezone

from asgiref.sync import sync_to_async
from django_celery_results.models import TaskResult


class MutationResult:
    """Simple result object for mutations."""

    def __init__(self, success: bool, message: str):
        self.success = success
        self.message = message


class TaskManagementService:
    """Service for managing Celery tasks."""

    async def cancel_all_pending_tasks(self) -> MutationResult:
        """
        Cancel all pending tasks by updating database records.

        Note: With SQLAlchemy/PostgreSQL broker, control.revoke() doesn't work.
        Instead, we mark tasks as REVOKED in the database directly.
        """
        try:
            # Update pending tasks to REVOKED status in database
            def revoke_pending_tasks():
                updated = TaskResult.objects.filter(
                    status__in=["PENDING", "STARTED", "RETRY"]
                ).update(status="REVOKED")
                return updated

            cancelled_count = await sync_to_async(revoke_pending_tasks)()

            return MutationResult(
                success=True,
                message=f"Successfully cancelled {cancelled_count} pending tasks",
            )

        except Exception as e:
            return MutationResult(
                success=False, message=f"Failed to cancel tasks: {str(e)}"
            )

    async def cancel_tasks_by_name(self, task_name: str) -> MutationResult:
        """Cancel all pending tasks with a specific name by updating database records."""
        try:
            # Update pending tasks with matching name to REVOKED status
            def revoke_tasks_by_name():
                updated = TaskResult.objects.filter(
                    status__in=["PENDING", "STARTED", "RETRY"],
                    task_name=task_name,
                ).update(status="REVOKED")
                return updated

            cancelled_count = await sync_to_async(revoke_tasks_by_name)()

            return MutationResult(
                success=True,
                message=f"Successfully cancelled {cancelled_count} tasks with name '{task_name}'",
            )

        except Exception as e:
            return MutationResult(
                success=False, message=f"Failed to cancel tasks: {str(e)}"
            )

    async def cancel_running_tasks_by_name(self, task_name: str) -> MutationResult:
        """Cancel running tasks by marking them as cancelled in the database."""
        try:
            from library_manager.models import TaskHistory

            # Find running tasks with the specified name using sync_to_async
            queryset = TaskHistory.objects.filter(
                type__iexact=task_name.replace("_", ""), status="RUNNING"
            )
            running_tasks: list = await sync_to_async(lambda: list(queryset))()

            cancelled_count = 0
            for task_history in running_tasks:
                try:
                    # Mark the task as cancelled using sync_to_async
                    task_history.status = "CANCELLED"
                    task_history.completed_at = timezone.now()
                    task_history.error_message = "Task cancelled by user"
                    await sync_to_async(task_history.save)()
                    cancelled_count += 1
                except Exception as e:
                    print(f"Failed to cancel running task {task_history.task_id}: {e}")

            return MutationResult(
                success=True,
                message=f"Successfully cancelled {cancelled_count} running tasks with name '{task_name}'",
            )

        except Exception as e:
            return MutationResult(
                success=False, message=f"Failed to cancel running tasks: {str(e)}"
            )

    async def cancel_all_tasks(self) -> MutationResult:
        """
        Cancel both pending and running tasks by updating database records.

        Note: With SQLAlchemy/PostgreSQL broker, we mark tasks as cancelled
        in the database instead of using control.revoke().
        """
        try:
            # Cancel pending tasks in Celery queue (from database)
            pending_result = await self.cancel_all_pending_tasks()

            # Cancel/clean up tasks marked as RUNNING in database
            from library_manager.models import TaskHistory

            queryset = TaskHistory.objects.filter(status="RUNNING")
            running_tasks: list = await sync_to_async(lambda: list(queryset))()
            cancelled_running_count = 0

            for task_history in running_tasks:
                try:
                    # Mark as cancelled in TaskHistory
                    task_history.status = "CANCELLED"
                    task_history.completed_at = timezone.now()
                    task_history.error_message = "Task cancelled by user"
                    await sync_to_async(task_history.save)()

                    # Also mark as REVOKED in TaskResult if it exists
                    # Capture task_id to avoid cell-var-from-loop
                    task_id_to_revoke = task_history.task_id

                    def revoke_task_result(tid: str = task_id_to_revoke) -> None:
                        TaskResult.objects.filter(task_id=tid).update(status="REVOKED")

                    await sync_to_async(revoke_task_result)()
                    cancelled_running_count += 1
                except Exception as e:
                    print(f"Failed to cancel running task {task_history.task_id}: {e}")

            # Safely parse pending count from message; default to 0 if parsing fails
            try:
                pending_count = int(pending_result.message.split()[2])
            except Exception:
                pending_count = 0

            total_cancelled = pending_count + cancelled_running_count

            return MutationResult(
                success=True,
                message=f"Successfully cancelled {total_cancelled} total tasks ({pending_count} pending, {cancelled_running_count} running)",
            )

        except Exception as e:
            return MutationResult(
                success=True, message=f"No tasks to cancel ({str(e)})"
            )

    def get_pending_tasks(self) -> list:
        """
        Get list of pending tasks from database.

        Note: Uses database queries since inspect.active() doesn't work
        with SQLAlchemy broker.
        """
        try:
            tasks = TaskResult.objects.filter(
                status__in=["PENDING", "STARTED", "RETRY"]
            ).values("task_id", "task_name", "task_args", "task_kwargs")

            result = []
            for task in tasks:
                task_info = {
                    "id": task.get("task_id"),
                    "name": task.get("task_name", "unknown"),
                    "args": task.get("task_args", []),
                    "kwargs": task.get("task_kwargs", {}),
                }
                result.append(task_info)

            return result
        except Exception as e:
            # Re-raise the exception as expected by the test
            raise e

    async def get_queue_status(self) -> Dict[str, Any]:
        """
        Get overall queue status information from database.

        Note: Uses database queries only since inspect.active() doesn't work
        with SQLAlchemy broker (PostgreSQL).
        """

        # Count pending/started tasks from database
        def count_active_tasks():
            return TaskResult.objects.filter(
                status__in=["PENDING", "STARTED", "RETRY"]
            ).count()

        total_tasks = await sync_to_async(count_active_tasks)()

        # Get task counts by name from database
        task_counts = await self.get_task_count_by_name()

        return {
            "total_pending_tasks": total_tasks,
            "task_counts": task_counts,
            "queue_size": total_tasks,
        }

    async def get_task_count_by_name(self) -> Dict[str, int]:
        """Get count of tasks by name from the database."""
        try:
            # Use sync_to_async for Django ORM operations
            queryset = TaskResult.objects.filter(
                status__in=["PENDING", "STARTED", "RETRY"]
            ).values("task_name")
            task_results: list = await sync_to_async(lambda: list(queryset))()

            task_counts = {}
            for task in task_results:
                task_name = task["task_name"]
                # Skip tasks with null or empty task names
                if not task_name:
                    continue
                if task_name not in task_counts:
                    task_counts[task_name] = 0
                task_counts[task_name] += 1

            return task_counts

        except Exception as e:
            print(f"Error getting task counts: {e}")
            return {}

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get status of a specific task from database.

        Checks TaskHistory first, then falls back to TaskResult.
        """
        try:
            from library_manager.models import TaskHistory

            # Try TaskHistory first
            try:
                task = await sync_to_async(TaskHistory.objects.get)(task_id=task_id)
                return {
                    "task_id": task.task_id,
                    "status": task.status,
                    "type": task.type,
                    "started_at": task.started_at,
                    "completed_at": task.completed_at,
                    "error_message": task.error_message,
                }
            except TaskHistory.DoesNotExist:
                # Try TaskResult as fallback
                def get_task_result():
                    try:
                        return TaskResult.objects.get(task_id=task_id)
                    except TaskResult.DoesNotExist:
                        return None

                task_result = await sync_to_async(get_task_result)()

                if task_result:
                    return {
                        "task_id": task_id,
                        "status": task_result.status,
                        "type": task_result.task_name or "UNKNOWN",
                        "started_at": task_result.date_created,
                        "completed_at": task_result.date_done,
                        "error_message": None,
                    }

                return {"error": "Task not found"}

        except Exception as e:
            return {"error": f"Error getting task status: {str(e)}"}

    async def clear_completed_tasks(self, days_old: int = 7) -> MutationResult:
        """Clear completed tasks older than specified days."""
        try:
            from datetime import timedelta

            cutoff_date = timezone.now() - timedelta(days=days_old)

            # Use sync_to_async for Django ORM operations
            deleted_count = await sync_to_async(
                lambda: TaskResult.objects.filter(
                    status__in=["SUCCESS", "FAILURE", "REVOKED"],
                    date_done__lt=cutoff_date,
                ).delete()
            )()

            return MutationResult(
                success=True,
                message=f"Successfully cleared {deleted_count[0]} completed tasks older than {days_old} days",
            )

        except Exception as e:
            return MutationResult(
                success=False, message=f"Failed to clear completed tasks: {str(e)}"
            )
