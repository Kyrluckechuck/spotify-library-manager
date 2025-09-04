"""
Celery app configuration for Spotify Library Manager.
"""

import os

import django

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# Initialize Django before creating Celery app

django.setup()

app = Celery("spotify_library_manager")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Optional configuration for task routing
app.conf.task_routes = {
    "library_manager.tasks.*": {"queue": "celery"},
}

# Task priority configuration
app.conf.task_default_priority = 5
app.conf.worker_prefetch_multiplier = 1
app.conf.task_acks_late = True
app.conf.worker_disable_rate_limits = True


@app.task(bind=True)  # type: ignore[misc]
def debug_task(self) -> None:  # type: ignore[no-untyped-def]
    """Debug task for testing Celery configuration."""
    print(f"Request: {self.request!r}")
