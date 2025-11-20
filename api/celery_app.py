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
