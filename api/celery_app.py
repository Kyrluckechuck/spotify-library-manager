"""
Celery app configuration for Spotify Library Manager.
"""

import logging
import os
import signal
import sys
from types import FrameType
from typing import Any, Optional

import django

import psutil
from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown, worker_shutdown

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Initialize Django before creating Celery app

django.setup()

# Configure logger for signal handlers (before Celery app creation)
logger = logging.getLogger("celery_diagnostics")

app = Celery("spotify_library_manager")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Task routing by service type to enable per-service concurrency control
app.conf.task_routes = {
    # Download tasks - route to 'downloads' queue (YouTube/spotdl - very rate-limited)
    "library_manager.tasks.download_missing_albums_for_artist": {"queue": "downloads"},
    "library_manager.tasks.download_single_album": {"queue": "downloads"},
    "library_manager.tasks.download_playlist": {"queue": "downloads"},
    "library_manager.tasks.download_extra_album_types_for_artist": {
        "queue": "downloads"
    },
    "library_manager.tasks.download_missing_tracked_artists": {"queue": "downloads"},
    # Spotify API tasks - route to 'spotify' queue (moderate rate limits)
    "library_manager.tasks.fetch_all_albums_for_artist": {"queue": "spotify"},
    "library_manager.tasks.sync_tracked_playlist": {"queue": "spotify"},
    "library_manager.tasks.sync_tracked_playlist_artists": {"queue": "spotify"},
    "library_manager.tasks.update_tracked_artists": {"queue": "spotify"},
    "library_manager.tasks.sync_tracked_playlists": {"queue": "spotify"},
    # Maintenance/cleanup tasks - route to default 'celery' queue
    "library_manager.tasks.cleanup_stuck_tasks_periodic": {"queue": "celery"},
    "library_manager.tasks.cleanup_celery_history": {"queue": "celery"},
    # Fallback for any other tasks
    "library_manager.tasks.*": {"queue": "celery"},
}

# Task priority configuration
app.conf.task_default_priority = 5
app.conf.worker_prefetch_multiplier = 1
app.conf.task_acks_late = True
app.conf.worker_disable_rate_limits = (
    False  # Enable rate limits for concurrency control
)

# Per-task rate limits to control concurrency (rate_limit format: "tasks/time_period")
# Download tasks: Limit to 2 concurrent (YouTube is very rate-sensitive)
app.conf.task_annotations = {
    "library_manager.tasks.download_missing_albums_for_artist": {"rate_limit": "2/s"},
    "library_manager.tasks.download_single_album": {"rate_limit": "2/s"},
    "library_manager.tasks.download_playlist": {"rate_limit": "2/s"},
    "library_manager.tasks.download_extra_album_types_for_artist": {
        "rate_limit": "2/s"
    },
    "library_manager.tasks.download_missing_tracked_artists": {"rate_limit": "2/s"},
    # Spotify tasks: More lenient (Spotify API is 180 req/min = 3/sec, so 5 concurrent is safe)
    "library_manager.tasks.fetch_all_albums_for_artist": {"rate_limit": "5/s"},
    "library_manager.tasks.sync_tracked_playlist": {"rate_limit": "5/s"},
    "library_manager.tasks.sync_tracked_playlist_artists": {"rate_limit": "5/s"},
    "library_manager.tasks.update_tracked_artists": {"rate_limit": "5/s"},
    "library_manager.tasks.sync_tracked_playlists": {"rate_limit": "5/s"},
}

# Ensure all task results include task names
app.conf.result_extended = True
app.conf.task_track_started = True


@app.task(bind=True, name="celery_app.debug_task")  # type: ignore[misc]
def debug_task(self: "Celery.Task") -> None:
    """Debug task for testing Celery configuration."""
    print(f"Request: {self.request!r}")


# ============================================================================
# Worker Diagnostics and Signal Handlers
# ============================================================================


def get_memory_info() -> dict:
    """Get current process memory usage information."""
    try:
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        return {
            "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size in MB
            "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size in MB
            "percent": process.memory_percent(),
        }
    except Exception as e:
        return {"error": str(e)}


def log_process_state(reason: str) -> None:
    """Log comprehensive process state for diagnostics."""
    try:
        process = psutil.Process(os.getpid())
        memory = get_memory_info()

        logger.critical(
            f"[WORKER DIAGNOSTIC] {reason} - "
            f"PID: {os.getpid()}, "
            f"Memory RSS: {memory.get('rss_mb', 'N/A'):.2f} MB, "
            f"Memory %: {memory.get('percent', 'N/A'):.2f}%, "
            f"Threads: {process.num_threads()}, "
            f"Status: {process.status()}"
        )
    except Exception as e:
        logger.error(f"[WORKER DIAGNOSTIC] Failed to log process state: {e}")


def signal_handler(signum: int, frame: Optional[FrameType]) -> None:
    """
    Handle termination signals to log diagnostic information before shutdown.

    This helps identify WHY the worker was killed (OOM, Docker, manual kill, etc.)
    """
    signal_names: dict[int, str] = {
        signal.SIGTERM: "SIGTERM (graceful shutdown requested)",
        signal.SIGINT: "SIGINT (interrupt from keyboard)",
        signal.SIGQUIT: "SIGQUIT (quit from keyboard)",
    }
    signal_name = signal_names.get(signum, f"Signal {signum}")

    log_process_state(f"Received {signal_name}")

    # Get active task info if available
    try:
        from celery import current_task

        if current_task and current_task.request:
            logger.critical(
                f"[WORKER DIAGNOSTIC] Active task: {current_task.name}, "
                f"Task ID: {current_task.request.id}"
            )
    except Exception as e:
        logger.warning(f"[WORKER DIAGNOSTIC] Could not get active task info: {e}")

    # Re-raise the signal to allow normal shutdown
    sys.exit(128 + signum)


# Register signal handlers for worker processes
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


# ============================================================================
# Worker Lifecycle Hooks
# ============================================================================


@worker_process_init.connect  # type: ignore[misc]
def worker_process_init_handler(sender: Any = None, **kwargs: Any) -> None:
    """Log when worker process starts (only if diagnostics enabled)."""
    from django.conf import settings

    diagnostics_enabled = getattr(settings, "worker_diagnostics_enabled", False)
    if diagnostics_enabled:
        logger.info(
            f"[WORKER LIFECYCLE] Worker process started - PID: {os.getpid()}, "
            f"Parent PID: {os.getppid()}"
        )
        log_process_state("Worker process initialization")


@worker_process_shutdown.connect  # type: ignore[misc]
def worker_process_shutdown_handler(sender: Any = None, **kwargs: Any) -> None:
    """Log when worker process shuts down (only if diagnostics enabled)."""
    from django.conf import settings

    diagnostics_enabled = getattr(settings, "worker_diagnostics_enabled", False)
    if diagnostics_enabled:
        logger.warning(
            f"[WORKER LIFECYCLE] Worker process shutting down - PID: {os.getpid()}"
        )
        log_process_state("Worker process shutdown")


@worker_shutdown.connect  # type: ignore[misc]
def worker_shutdown_handler(sender: Any = None, **kwargs: Any) -> None:
    """Log when main worker shuts down (only if diagnostics enabled)."""
    from django.conf import settings

    diagnostics_enabled = getattr(settings, "worker_diagnostics_enabled", False)
    if diagnostics_enabled:
        logger.warning(
            f"[WORKER LIFECYCLE] Main worker shutting down - PID: {os.getpid()}"
        )
        log_process_state("Main worker shutdown")
