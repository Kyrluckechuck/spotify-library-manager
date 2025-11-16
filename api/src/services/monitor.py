"""Monitor service for tracking task progress."""

import time
from typing import Any, Dict


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
