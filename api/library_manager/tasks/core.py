"""Core task utilities and helper functions.

This module contains shared utilities used across all task modules:
- Task history management (create, update, complete)
- Progress tracking and cancellation checks
- Memory usage logging
- Download capability validation
"""

import os
import uuid
from functools import wraps
from typing import Any, Callable, Optional, cast

from django.conf import settings

import psutil
from celery.utils.log import get_task_logger
from celery_app import app as celery_app  # noqa: F401 - re-exported
from downloader.spotdl_wrapper import SpotdlWrapper
from lib.config_class import Config

from ..models import TaskHistory


class TaskCancelledException(Exception):
    """Raised when a task has been cancelled and should stop execution."""


# Initialize SpotdlWrapper
spotdl_wrapper = SpotdlWrapper(Config())

# Initialize Celery logger
logger = get_task_logger(__name__)


def log_memory_usage(context: str, task_id: Optional[str] = None) -> None:
    """Log current memory usage for diagnostics (only if enabled in settings)."""
    diagnostics_enabled = getattr(settings, "worker_diagnostics_enabled", False)
    if not diagnostics_enabled:
        return

    try:
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        rss_mb = memory_info.rss / 1024 / 1024
        memory_percent = process.memory_percent()

        log_msg = (
            f"[MEMORY] {context} - "
            f"RSS: {rss_mb:.2f} MB, "
            f"Memory %: {memory_percent:.2f}%"
        )
        if task_id:
            log_msg += f", Task: {task_id}"

        logger.info(log_msg)
    except Exception as e:
        logger.warning(f"[MEMORY] Failed to log memory usage: {e}")


def create_task_history(
    task_id: Optional[str] = None,
    task_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    task_name: Optional[str] = None,
) -> TaskHistory:
    """Create a task history record for tracking task execution"""
    if task_id is None:
        # Create task ID if not provided
        entity_type_str = entity_type or "unknown"
        if entity_id:
            generated_task_id = f"{task_type}-{entity_type_str.lower()}-{entity_id}"
        else:
            generated_task_id = f"{task_name or 'unknown'}-{uuid.uuid4().hex[:8]}"
    else:
        generated_task_id = task_id

    # Check if task history already exists for this task
    existing_task = TaskHistory.objects.filter(task_id=generated_task_id).first()
    if existing_task:
        return existing_task

    # Log memory usage at task start
    log_memory_usage(f"Task created: {task_type}/{entity_type}", generated_task_id)

    # Create new task history record
    task_history = TaskHistory(
        task_id=generated_task_id,
        type=task_type or "UNKNOWN",
        entity_id=str(entity_id) if entity_id else "unknown",
        entity_type=entity_type or "UNKNOWN",
        status="PENDING",
    )
    task_history.save()
    return task_history


def update_task_progress(
    task_history: TaskHistory, progress: float, message: Optional[str] = None
) -> None:
    """Update task progress, heartbeat, and add log message"""
    task_history.status = "RUNNING"
    task_history.progress_percentage = progress
    task_history.update_heartbeat()  # Update heartbeat on progress
    if message:
        task_history.add_log_message(message)
    task_history.save()


def update_task_heartbeat(task_history: TaskHistory) -> None:
    """Update task heartbeat (no log message)"""
    task_history.update_heartbeat()


def complete_task(
    task_history: TaskHistory, success: bool = True, error_message: Optional[str] = None
) -> None:
    """Mark task as completed or failed"""
    # Log memory usage at task completion
    status_str = "completed" if success else f"failed: {error_message}"
    log_memory_usage(f"Task {status_str}", task_history.task_id)

    if success:
        task_history.mark_completed()
    else:
        task_history.mark_failed(error_message)


def check_task_cancellation(task_history: TaskHistory) -> bool:
    """Check if the task has been cancelled by checking the database status."""
    # Refresh from database to get latest status
    task_history.refresh_from_db()
    status_str: str = cast(str, task_history.status)
    return status_str == "CANCELLED"


def check_if_cancelled(task_id: str) -> None:
    """
    Check if task has been cancelled. Raise TaskCancelledException if it has.

    This function checks both TaskResult (for queued tasks marked as REVOKED)
    and TaskHistory (for running tasks marked as CANCELLED).

    Call this at safe checkpoints in long-running tasks (e.g., after each song/album).

    Args:
        task_id: The Celery task ID to check

    Raises:
        TaskCancelledException: If the task has been cancelled
    """
    from django_celery_results.models import TaskResult

    # Check TaskResult first (for pending/queued tasks marked as REVOKED)
    try:
        task_result = TaskResult.objects.filter(task_id=task_id).first()
        if task_result and task_result.status == "REVOKED":
            logger.info(f"Task {task_id} cancelled via TaskResult (REVOKED)")
            raise TaskCancelledException(f"Task {task_id} was cancelled")
    except TaskResult.DoesNotExist:
        pass

    # Check TaskHistory (for running tasks marked as CANCELLED)
    try:
        task_history = TaskHistory.objects.filter(task_id=task_id).first()
        if task_history and task_history.status == "CANCELLED":
            logger.info(f"Task {task_id} cancelled via TaskHistory (CANCELLED)")
            raise TaskCancelledException(f"Task {task_id} was cancelled")
    except TaskHistory.DoesNotExist:
        pass


def skip_if_cancelled(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator that checks if task is cancelled before starting execution.

    If the task has been cancelled (REVOKED or CANCELLED status), it will be skipped
    and return a cancellation result instead of executing.

    Usage:
        @shared_task(bind=True)
        @skip_if_cancelled
        def my_task(self, arg1, arg2):
            # Task code here
    """

    @wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        task_id = self.request.id
        try:
            check_if_cancelled(task_id)
        except TaskCancelledException:
            logger.info(f"Task {task_id} skipped - already cancelled before start")
            return {
                "status": "cancelled",
                "skipped": True,
                "message": "Task was cancelled before execution started",
            }

        # Execute task
        return func(self, *args, **kwargs)

    return wrapper


def check_and_update_progress(
    task_history: TaskHistory, progress: float, message: Optional[str] = None
) -> bool:
    """Update task progress and check for cancellation. Returns True if cancelled."""
    if check_task_cancellation(task_history):
        return True

    update_task_progress(task_history, progress, message)
    return False


def require_download_capability(task_history: Optional[TaskHistory] = None) -> None:
    """Check authentication status and block task execution if downloads are not possible.

    This function verifies that the system has valid authentication (cookies) before
    allowing download tasks to proceed. If authentication is invalid or expired, the
    task is failed immediately to prevent wasted API calls.

    Args:
        task_history: Optional task history to update with failure status if auth fails

    Raises:
        RuntimeError: If downloads are not possible due to authentication issues
    """
    from src.services.system_health import SystemHealthService

    can_download, reason = SystemHealthService.is_download_capable()
    if not can_download:
        error_msg = f"Cannot download: {reason}"
        logger.error(error_msg)
        if task_history:
            task_history.status = "FAILED"
            task_history.add_log_message(error_msg)
            task_history.save()
        raise RuntimeError(error_msg)
