"""
Service for fetching periodic task schedules from Celery Beat.
"""

from typing import Any, List, Optional, Set

from asgiref.sync import sync_to_async
from django_celery_beat.models import PeriodicTask as DjangoPeriodicTask

from ..graphql_types.models import PeriodicTask

# Core tasks that should not be toggled by users - these are essential for system health
CORE_TASK_NAMES: Set[str] = {
    "celery.backend_cleanup",
    "cleanup-celery-history",
    "cleanup-stale-tasks",
    "cleanup-old-downloads",
}


class PeriodicTaskService:
    """Service for fetching Celery Beat periodic task schedules."""

    def _format_crontab(self, crontab: Optional[Any]) -> str:
        """Format a CrontabSchedule into a human-readable string."""
        if not crontab:
            return "Not scheduled"

        minute = crontab.minute
        hour = crontab.hour
        day_of_month = crontab.day_of_month
        month = crontab.month_of_year
        day_of_week = crontab.day_of_week

        # Build human-readable description
        parts: List[str] = []

        # Time - check for interval patterns first
        if hour.startswith("*/"):
            interval = hour[2:]
            if minute == "0":
                parts.append(f"every {interval} hours")
            else:
                parts.append(f"every {interval} hours at minute {minute}")
        elif minute.startswith("*/"):
            interval = minute[2:]
            parts.append(f"every {interval} minutes")
        elif hour == "*" and minute == "0":
            # Every hour at the top of the hour
            parts.append("every hour")
        elif minute == "0" and hour != "*":
            parts.append(f"at {hour}:00")
        elif minute != "*" and hour != "*":
            parts.append(f"at {hour}:{minute.zfill(2)}")

        # Day of week
        day_names = {
            "0": "Sunday",
            "1": "Monday",
            "2": "Tuesday",
            "3": "Wednesday",
            "4": "Thursday",
            "5": "Friday",
            "6": "Saturday",
        }
        if day_of_week != "*":
            if day_of_week in day_names:
                parts.append(f"on {day_names[day_of_week]}s")
            else:
                parts.append(f"on day {day_of_week}")

        # Day of month
        if day_of_month != "*":
            parts.append(f"on day {day_of_month}")

        # Month
        if month != "*":
            parts.append(f"in month {month}")

        if not parts:
            # Fallback to cron notation
            return f"{minute} {hour} {day_of_month} {month} {day_of_week}"

        return " ".join(parts)

    def _format_interval(self, interval: Optional[Any]) -> str:
        """Format an IntervalSchedule into a human-readable string."""
        if not interval:
            return "Not scheduled"

        period = interval.period
        every = interval.every

        if every == 1:
            # Singular form
            period_map = {
                "days": "day",
                "hours": "hour",
                "minutes": "minute",
                "seconds": "second",
            }
            return f"every {period_map.get(period, period)}"

        return f"every {every} {period}"

    def _to_graphql_type(self, task: DjangoPeriodicTask) -> PeriodicTask:
        """Convert Django PeriodicTask to GraphQL type."""
        # Determine schedule description
        if task.crontab:
            schedule_desc = self._format_crontab(task.crontab)
        elif task.interval:
            schedule_desc = self._format_interval(task.interval)
        elif task.clocked:
            schedule_desc = f"once at {task.clocked.clocked_time}"
        elif task.solar:
            schedule_desc = f"solar: {task.solar.event}"
        else:
            schedule_desc = "No schedule"

        return PeriodicTask(
            id=task.id,
            name=task.name,
            task=task.task,
            enabled=task.enabled,
            is_core=task.name in CORE_TASK_NAMES,
            description=task.description or None,
            schedule_description=schedule_desc,
            last_run_at=task.last_run_at.isoformat() if task.last_run_at else None,
            total_run_count=task.total_run_count,
        )

    async def get_all(self) -> List[PeriodicTask]:
        """Get all periodic tasks."""

        def fetch_tasks() -> List[PeriodicTask]:
            tasks = list(
                DjangoPeriodicTask.objects.select_related(
                    "crontab", "interval", "clocked", "solar"
                ).order_by("name")
            )
            return [self._to_graphql_type(task) for task in tasks]

        return await sync_to_async(fetch_tasks)()

    async def toggle_enabled(
        self, task_id: int, enabled: bool
    ) -> Optional[PeriodicTask]:
        """Toggle the enabled state of a periodic task.

        Returns None if the task doesn't exist or is a core task.
        """

        def do_toggle() -> Optional[PeriodicTask]:
            try:
                task = DjangoPeriodicTask.objects.select_related(
                    "crontab", "interval", "clocked", "solar"
                ).get(id=task_id)
            except DjangoPeriodicTask.DoesNotExist:
                return None

            # Prevent toggling core tasks
            if task.name in CORE_TASK_NAMES:
                return None

            task.enabled = enabled
            task.save(update_fields=["enabled"])
            return self._to_graphql_type(task)

        return await sync_to_async(do_toggle)()

    async def run_now(self, task_id: int) -> bool:
        """Trigger a periodic task to run immediately.

        Returns True if the task was queued successfully, False otherwise.
        """
        from celery_app import app as celery_app

        def do_run() -> bool:
            try:
                task = DjangoPeriodicTask.objects.get(id=task_id)
            except DjangoPeriodicTask.DoesNotExist:
                return False

            # Use send_task to queue the task by name - this works even if the
            # task isn't registered in the current process (web vs worker)
            celery_app.send_task(task.task)
            return True

        return await sync_to_async(do_run)()

    async def get_enabled(self) -> List[PeriodicTask]:
        """Get only enabled periodic tasks."""

        def fetch_tasks() -> List[PeriodicTask]:
            tasks = list(
                DjangoPeriodicTask.objects.filter(enabled=True)
                .select_related("crontab", "interval", "clocked", "solar")
                .order_by("name")
            )
            return [self._to_graphql_type(task) for task in tasks]

        return await sync_to_async(fetch_tasks)()
