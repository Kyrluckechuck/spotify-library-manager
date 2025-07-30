from django.core.management.base import BaseCommand

from library_manager.models import TaskHistory


class Command(BaseCommand):
    help = "Clean up stuck tasks that have exceeded their timeout"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be cleaned up without actually doing it",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force cleanup even if task is not detected as stuck",
        )

    def handle(self, *args, **options) -> None:
        dry_run = options["dry_run"]
        force = options["force"]

        if dry_run:
            self.stdout.write("DRY RUN - No changes will be made")

        # Find stuck tasks
        stuck_tasks = TaskHistory.objects.filter(status="RUNNING")
        stuck_count = 0

        for task in stuck_tasks:
            is_stuck = task.is_stuck() or force
            if is_stuck:
                stuck_count += 1
                if dry_run:
                    self.stdout.write(f"Would mark as stuck: {task}")
                    if force:
                        self.stdout.write("  (forced cleanup)")
                else:
                    reason = "Task timeout - automatic cleanup"
                    if force:
                        reason = "Task timeout - forced cleanup"
                    task.mark_stuck(reason)
                    self.stdout.write(f"Marked as stuck: {task}")

        if stuck_count == 0:
            self.stdout.write(self.style.SUCCESS("No stuck tasks found"))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Processed {stuck_count} stuck task(s)")
            )
