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
    "cleanup-old-downloads": {
        "task": "library_manager.tasks.cleanup_old_downloads_task",
        "schedule": crontab(minute=45, hour="*/8"),  # Every 8 hours, 45 minutes past
        "options": {"priority": 0},
    },
    "retry-failed-playlist-songs": {
        "task": "library_manager.tasks.validate_undownloaded_songs",
        "schedule": crontab(
            minute=0, hour=3, day_of_week=0
        ),  # Weekly on Sunday at 3 AM
        "options": {"priority": 1},
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
