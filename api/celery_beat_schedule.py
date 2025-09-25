"""
Celery Beat schedule configuration for periodic tasks.
"""

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "sync-all-playlists": {
        "task": "library_manager.tasks.sync_all_tracked_playlists_task",
        "schedule": crontab(minute=0, hour="*/8"),  # Every 8 hours
        "options": {"priority": 1},
    },
    "cleanup-old-downloads": {
        "task": "library_manager.tasks.cleanup_old_downloads_task",
        "schedule": crontab(minute=45, hour="*/8"),  # Every 8 hours, 45 minutes past
        "options": {"priority": 0},
    },
    "update-playlists-task": {
        "task": "library_manager.tasks.update_playlists_task",
        "schedule": crontab(minute=0, hour="*/4"),  # Every 4 hours
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
