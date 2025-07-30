from django.core.management.base import BaseCommand

from library_manager.models import TaskHistory


class Command(BaseCommand):
    help = "Clean up old completed/failed tasks to manage storage"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Number of days to keep completed/failed tasks (default: 30)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be cleaned up without actually doing it",
        )
        parser.add_argument(
            "--stats",
            action="store_true",
            help="Show storage statistics before cleanup",
        )

    def handle(self, *args, **options) -> None:
        days_to_keep = options["days"]
        dry_run = options["dry_run"]
        show_stats = options["stats"]

        if show_stats:
            stats = TaskHistory.get_storage_stats()
            self.stdout.write("TaskHistory Storage Statistics:")
            self.stdout.write(f'  Total tasks: {stats["total_tasks"]}')
            self.stdout.write(f'  Completed tasks: {stats["completed_tasks"]}')
            self.stdout.write(f'  Failed tasks: {stats["failed_tasks"]}')
            self.stdout.write(f'  Running tasks: {stats["running_tasks"]}')
            self.stdout.write(f'  Pending tasks: {stats["pending_tasks"]}')
            self.stdout.write(f'  Tasks with logs: {stats["tasks_with_logs"]}')
            self.stdout.write(
                f'  Average logs per task: {stats["average_logs_per_task"]}'
            )
            self.stdout.write("")

        if dry_run:
            self.stdout.write(
                f"DRY RUN - Would delete completed/failed tasks older than {days_to_keep} days"
            )

        # Find old tasks that would be deleted
        from datetime import timedelta

        from django.utils import timezone

        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        old_tasks = TaskHistory.objects.filter(
            status__in=["COMPLETED", "FAILED"], started_at__lt=cutoff_date
        )

        old_count = old_tasks.count()

        if old_count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"No completed/failed tasks older than {days_to_keep} days found"
                )
            )
            return

        if dry_run:
            self.stdout.write(f"Would delete {old_count} old tasks:")
            for task in old_tasks[:10]:  # Show first 10
                self.stdout.write(f"  - {task} (started: {task.started_at})")
            if old_count > 10:
                self.stdout.write(f"  ... and {old_count - 10} more")
        else:
            deleted_count = TaskHistory.cleanup_old_tasks(days_to_keep)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Deleted {deleted_count} old tasks (older than {days_to_keep} days)"
                )
            )
