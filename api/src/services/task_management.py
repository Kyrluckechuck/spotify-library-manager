from typing import Dict, List

from huey.contrib.djhuey import HUEY

from ..graphql_types.models import MutationResult


class TaskManagementService:
    """Service for managing Huey background tasks."""

    def get_pending_tasks(self) -> List[Dict[str, any]]:
        """Get all pending tasks with their details."""
        pending_tasks = HUEY.pending()
        task_details = []

        for task in pending_tasks:
            task_details.append({
                "id": str(task.id),
                "name": task.name,
                "args": task.args,
                "kwargs": task.kwargs,
                "priority": getattr(task, 'priority', None),
                "created_at": task.created_at.isoformat() if task.created_at else None,
            })

        return task_details

    def get_task_count_by_name(self) -> Dict[str, int]:
        """Get count of pending tasks grouped by task name."""
        pending_tasks = HUEY.pending()
        task_counts = {}

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
                message=f"Successfully cancelled {cancelled_count} pending tasks"
            )

        except Exception as e:
            return MutationResult(
                success=False,
                message=f"Failed to cancel tasks: {str(e)}"
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
                message=f"Successfully cancelled {cancelled_count} tasks with name '{task_name}'"
            )

        except Exception as e:
            return MutationResult(
                success=False,
                message=f"Failed to cancel tasks: {str(e)}"
            )

    def get_queue_status(self) -> Dict[str, any]:
        """Get overall queue status information."""
        pending_tasks = HUEY.pending()
        task_counts = self.get_task_count_by_name()

        return {
            "total_pending_tasks": len(pending_tasks),
            "task_counts": task_counts,
            "queue_size": len(pending_tasks),
        } 