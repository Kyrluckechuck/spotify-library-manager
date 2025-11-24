"""
Celery Beat schedule configuration for periodic tasks.
"""

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "sync-all-playlists": {
        "task": "library_manager.tasks.sync_tracked_playlists",
        "schedule": crontab(minute=0, hour="*/8"),  # Every 8 hours
        "options": {"priority": 1},
    },
    "retry-failed-playlist-songs": {
        "task": "library_manager.tasks.validate_undownloaded_songs",
        "schedule": crontab(
            minute=0, hour=3, day_of_week=0
        ),  # Weekly on Sunday at 3 AM
        "options": {"priority": 1},
    },
    "retry-failed-songs": {
        "task": "library_manager.tasks.retry_failed_songs",
        "schedule": crontab(minute=0, hour="*/6"),  # Every 6 hours
        "options": {"priority": 2},
    },
    "queue-missing-albums-for-tracked-artists": {
        "task": "library_manager.tasks.queue_missing_albums_for_tracked_artists",
        "schedule": crontab(minute=0),  # Every hour
        "options": {"priority": 3},
    },
    "cleanup-celery-history": {
        "task": "library_manager.tasks.cleanup_celery_history",
        "schedule": crontab(minute=0, hour=6),  # Daily at 6 AM
        "options": {"priority": 10},
    },
    "cleanup-stale-tasks": {
        "task": "library_manager.tasks.cleanup_stuck_tasks_periodic",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
        "options": {"priority": 5},
    },
}
