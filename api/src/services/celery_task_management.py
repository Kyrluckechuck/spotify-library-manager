"""
Celery task management service for handling task operations.
"""

from typing import Any, Dict, List

from django.utils import timezone

from asgiref.sync import sync_to_async
from celery import current_app
from django_celery_results.models import TaskResult


class MutationResult:
    """Simple result object for mutations."""

    def __init__(self, success: bool, message: str):
        self.success = success
        self.message = message


class CeleryTaskManagementService:
    """Service for managing Celery tasks."""

    async def cancel_all_pending_tasks(self) -> MutationResult:
        """Cancel all pending tasks in the Celery queue."""
        try:
            # Get pending tasks from Celery
            inspect = current_app.control.inspect()
            active_tasks = inspect.active() or {}
            scheduled_tasks = inspect.scheduled() or {}
            cancelled_count = 0

            # Cancel active tasks
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    try:
                        current_app.control.revoke(task["id"], terminate=True)
                        cancelled_count += 1
                    except Exception as e:
                        print(f"Failed to cancel active task {task['id']}: {e}")

            # Cancel scheduled tasks
            for worker, tasks in scheduled_tasks.items():
                for task in tasks:
                    try:
                        current_app.control.revoke(task["id"], terminate=True)
                        cancelled_count += 1
                    except Exception as e:
                        print(f"Failed to cancel scheduled task {task['id']}: {e}")

            return MutationResult(
                success=True,
                message=f"Successfully cancelled {cancelled_count} pending tasks",
            )

        except Exception as e:
            return MutationResult(
                success=False, message=f"Failed to cancel tasks: {str(e)}"
            )

    async def cancel_tasks_by_name(self, task_name: str) -> MutationResult:
        """Cancel all pending tasks with a specific name."""
        try:
            inspect = current_app.control.inspect()
            active_tasks = inspect.active() or {}
            cancelled_count = 0

            for worker, tasks in active_tasks.items():
                for task in tasks:
                    if task_name.lower() in task.get("name", "").lower():
                        try:
                            current_app.control.revoke(task["id"], terminate=True)
                            cancelled_count += 1
                        except Exception as e:
                            print(f"Failed to cancel task {task['id']}: {e}")

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

            # Find running tasks with the specified name
            running_tasks: list = await sync_to_async(list)(
                TaskHistory.objects.filter(
                    type__iexact=task_name.replace("_", ""), status="RUNNING"
                )
            )

            cancelled_count = 0
            for task_history in running_tasks:
                try:
                    # Mark the task as cancelled
                    task_history.status = "CANCELLED"
                    task_history.completed_at = timezone.now()
                    task_history.error_message = "Task cancelled by user"
                    await sync_to_async(task_history.save)()

                    # Also revoke from Celery
                    try:
                        current_app.control.revoke(task_history.task_id, terminate=True)
                    except Exception:
                        pass  # Task might not be in Celery queue anymore

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

    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get list of pending tasks from Celery queue."""
        try:
            inspect = current_app.control.inspect()
            active_tasks = inspect.active() or {}
            scheduled_tasks = inspect.scheduled() or {}
            result = []

            # Process active tasks
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    task_info = {
                        "id": task.get("id"),
                        "name": task.get("name", "unknown"),
                        "args": task.get("args", []),
                        "kwargs": task.get("kwargs", {}),
                        "worker": worker,
                        "status": "active",
                    }
                    result.append(task_info)

            # Process scheduled tasks
            for worker, tasks in scheduled_tasks.items():
                for task in tasks:
                    task_info = {
                        "id": task.get("id"),
                        "name": task.get("name", "unknown"),
                        "args": task.get("args", []),
                        "kwargs": task.get("kwargs", {}),
                        "worker": worker,
                        "status": "scheduled",
                        "eta": task.get("eta"),
                    }
                    result.append(task_info)

            return result
        except Exception as e:
            raise e

    async def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status information."""
        try:
            inspect = current_app.control.inspect()
            active_tasks = inspect.active() or {}
            scheduled_tasks = inspect.scheduled() or {}

            total_active = sum(len(tasks) for tasks in active_tasks.values())
            total_scheduled = sum(len(tasks) for tasks in scheduled_tasks.values())

            task_counts = await self.get_task_count_by_name()

            return {
                "total_active_tasks": total_active,
                "total_scheduled_tasks": total_scheduled,
                "total_pending_tasks": total_active + total_scheduled,
                "task_counts": task_counts,
                "workers": list(active_tasks.keys()),
            }
        except Exception as e:
            return {
                "total_active_tasks": 0,
                "total_scheduled_tasks": 0,
                "total_pending_tasks": 0,
                "task_counts": {},
                "workers": [],
                "error": str(e),
            }

    async def get_task_count_by_name(self) -> Dict[str, int]:
        """Get count of tasks by name from the database."""
        try:
            from library_manager.models import TaskHistory

            # Use sync_to_async for Django ORM operations
            tasks: list = await sync_to_async(
                lambda: list(TaskHistory.objects.values("type"))
            )()

            task_counts = {}
            for task in tasks:
                task_type = task["type"]
                if task_type not in task_counts:
                    task_counts[task_type] = 0
                task_counts[task_type] += 1

            return task_counts

        except Exception as e:
            print(f"Error getting task counts: {e}")
            return {}

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a specific task."""
        try:
            from library_manager.models import TaskHistory

            # Try to find the task in the database
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
                # Check if it's in Celery
                inspect = current_app.control.inspect()
                active_tasks = inspect.active() or {}

                for worker, tasks in active_tasks.items():
                    for task in tasks:
                        # task is a dict from Celery's active task list
                        task_dict: dict = task
                        if task_dict.get("id") == task_id:
                            return {
                                "task_id": task_id,
                                "status": "ACTIVE",
                                "type": task_dict.get("name", "UNKNOWN"),
                                "worker": worker,
                                "started_at": None,
                                "completed_at": None,
                                "error_message": None,
                            }

                return {"error": "Task not found"}

        except Exception as e:
            return {"error": f"Error getting task status: {str(e)}"}

    async def clear_completed_tasks(self, days_old: int = 7) -> MutationResult:
        """Clear completed tasks older than specified days."""
        try:
            from datetime import timedelta

            from library_manager.models import TaskHistory

            cutoff_date = timezone.now() - timedelta(days=days_old)

            # Clear from TaskHistory
            deleted_count = await sync_to_async(
                lambda: TaskHistory.objects.filter(
                    status__in=["COMPLETED", "FAILED", "CANCELLED"],
                    completed_at__lt=cutoff_date,
                ).delete()
            )()

            # Clear from Celery results
            try:
                celery_deleted = await sync_to_async(
                    lambda: TaskResult.objects.filter(
                        date_done__lt=cutoff_date
                    ).delete()
                )()
                total_deleted = deleted_count[0] + celery_deleted[0]
            except Exception:
                total_deleted = deleted_count[0]

            return MutationResult(
                success=True,
                message=f"Successfully cleared {total_deleted} completed tasks older than {days_old} days",
            )

        except Exception as e:
            return MutationResult(
                success=False, message=f"Failed to clear completed tasks: {str(e)}"
            )
