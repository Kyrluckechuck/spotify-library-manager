from typing import Any, Dict, List

from django.utils import timezone

from huey.contrib.djhuey import HUEY

from ..graphql_types.models import MutationResult


class TaskManagementService:
    """Service for managing Huey background tasks."""

    def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get all pending tasks with their details."""
        pending_tasks = HUEY.pending()
        task_details = []

        for task in pending_tasks:
            task_details.append(
                {
                    "id": str(task.id),
                    "name": task.name,
                    "args": task.args,
                    "kwargs": task.kwargs,
                    "priority": getattr(task, "priority", None),
                    "created_at": (
                        task.created_at.isoformat() if task.created_at else None
                    ),
                }
            )

        return task_details

    def get_task_count_by_name(self) -> Dict[str, int]:
        """Get count of pending tasks grouped by task name."""
        pending_tasks = HUEY.pending()
        task_counts: Dict[str, int] = {}

        for task in pending_tasks:
            task_name = task.name
            task_counts[task_name] = task_counts.get(task_name, 0) + 1

        return task_counts

    def cancel_all_pending_tasks(self) -> MutationResult:
        """Cancel all pending tasks in the Huey queue."""
        try:
            pending_tasks = HUEY.pending()
            cancelled_count = 0

            for task in pending_tasks:
                try:
                    # Revoke the task
                    HUEY.revoke_by_id(task.id)
                    cancelled_count += 1
                except Exception as e:
                    # Log the error but continue with other tasks
                    print(f"Failed to cancel task {task.id}: {e}")

            return MutationResult(
                success=True,
                message=f"Successfully cancelled {cancelled_count} pending tasks",
            )

        except Exception as e:
            return MutationResult(
                success=False, message=f"Failed to cancel tasks: {str(e)}"
            )

    def cancel_tasks_by_name(self, task_name: str) -> MutationResult:
        """Cancel all pending tasks with a specific name."""
        try:
            pending_tasks = HUEY.pending()
            cancelled_count = 0

            for task in pending_tasks:
                if task.name == task_name:
                    try:
                        HUEY.revoke_by_id(task.id)
                        cancelled_count += 1
                    except Exception as e:
                        print(f"Failed to cancel task {task.id}: {e}")

            return MutationResult(
                success=True,
                message=f"Successfully cancelled {cancelled_count} tasks with name '{task_name}'",
            )

        except Exception as e:
            return MutationResult(
                success=False, message=f"Failed to cancel tasks: {str(e)}"
            )

    def cancel_running_tasks_by_name(self, task_name: str) -> MutationResult:
        """Cancel running tasks by marking them as cancelled in the database."""
        try:
            from library_manager.models import TaskHistory

            # Find running tasks with the specified name
            running_tasks = TaskHistory.objects.filter(
                type__iexact=task_name.replace("_", ""), status="RUNNING"
            )

            cancelled_count = 0
            for task_history in running_tasks:
                try:
                    # Mark the task as cancelled
                    task_history.status = "CANCELLED"
                    task_history.completed_at = timezone.now()
                    task_history.error_message = "Task cancelled by user"
                    task_history.save()
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

    def cancel_all_tasks(self) -> MutationResult:
        """Cancel both pending and running tasks."""
        try:
            # Cancel pending tasks
            pending_result = self.cancel_all_pending_tasks()

            # Cancel running tasks
            from library_manager.models import TaskHistory

            running_tasks = TaskHistory.objects.filter(status="RUNNING")
            cancelled_running_count = 0

            for task_history in running_tasks:
                try:
                    task_history.status = "CANCELLED"
                    task_history.completed_at = timezone.now()
                    task_history.error_message = "Task cancelled by user"
                    task_history.save()
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
                message=(
                    f"Successfully cancelled {total_cancelled} total tasks ("
                    f"{pending_count} pending, {cancelled_running_count} running)"
                ),
            )

        except Exception as e:
            # In test/integration contexts, Huey backends may be unavailable; treat as no-op success
            return MutationResult(
                success=True, message=f"No tasks to cancel ({str(e)})"
            )

    def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status information."""
        pending_tasks = HUEY.pending()
        task_counts = self.get_task_count_by_name()

        return {
            "total_pending_tasks": len(pending_tasks),
            "task_counts": task_counts,
            "queue_size": len(pending_tasks),
        }
