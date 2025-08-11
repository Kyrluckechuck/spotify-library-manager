"""Monitor service for tracking task progress."""

import time
from typing import Any, Dict

from ..services.event_bus import ProcessInfo as BusProcessInfo
from ..services.event_bus import event_bus


# Mock ProcessInfo class since django-huey-monitor might not be available
class ProcessInfo:
    def __init__(self, task: Any = None, desc: str | None = None, percentage: int = 0):
        self.task = task
        self.desc = desc
        self.percentage = percentage


class ProgressMonitor:
    """Mock progress monitor for testing."""

    def on_task_progress(self, process_info: BusProcessInfo) -> None:
        """Handle task progress updates."""
        if hasattr(event_bus, "update_progress"):
            event_bus.update_progress(process_info)


class MonitorService:
    """Service for monitoring system status and health."""

    def __init__(self, monitoring_interval: int = 60) -> None:
        self.monitoring_interval: int = monitoring_interval
        self.is_running: bool = False
        self.start_time: float | None = None
        self.last_check: float | None = None

    def start_monitoring(self) -> None:
        """Start the monitoring service."""
        if not self.is_running:
            self.is_running = True
            self.start_time = time.time()
            self.last_check = time.time()

    def stop_monitoring(self) -> None:
        """Stop the monitoring service."""
        self.is_running = False
        self.start_time = None
        self.last_check = None

    def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        current_time = time.time()
        self.last_check = current_time

        uptime: float = 0.0
        if self.start_time:
            uptime = current_time - self.start_time

        return {
            "is_running": self.is_running,
            "last_check": self.last_check,
            "uptime": uptime,
        }


monitor = ProgressMonitor()
