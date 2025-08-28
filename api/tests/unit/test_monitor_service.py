"""Unit tests for monitor service."""

import pytest

from src.services.monitor import MonitorService


@pytest.fixture
def monitor_service():
    return MonitorService()


class TestMonitorService:
    """Test MonitorService functionality."""

    def test_monitor_service_initialization(self, monitor_service):
        """Test MonitorService can be initialized."""
        assert monitor_service is not None
        assert hasattr(monitor_service, "start_monitoring")
        assert hasattr(monitor_service, "stop_monitoring")
        assert hasattr(monitor_service, "get_status")

    def test_monitor_service_default_state(self, monitor_service):
        """Test MonitorService default state."""
        assert monitor_service.is_running is False
        assert monitor_service.monitoring_interval == 60  # Default interval

    def test_start_monitoring(self, monitor_service):
        """Test starting monitoring."""
        monitor_service.start_monitoring()

        assert monitor_service.is_running is True

    def test_stop_monitoring(self, monitor_service):
        """Test stopping monitoring."""
        monitor_service.start_monitoring()
        monitor_service.stop_monitoring()

        assert monitor_service.is_running is False

    def test_get_status_when_not_running(self, monitor_service):
        """Test getting status when not running."""
        status = monitor_service.get_status()

        assert status["is_running"] is False
        assert "last_check" in status
        assert "uptime" in status

    def test_get_status_when_running(self, monitor_service):
        """Test getting status when running."""
        monitor_service.start_monitoring()
        status = monitor_service.get_status()

        assert status["is_running"] is True
        assert "last_check" in status
        assert "uptime" in status

    def test_start_monitoring_when_already_running(self, monitor_service):
        """Test starting monitoring when already running."""
        monitor_service.start_monitoring()
        monitor_service.start_monitoring()  # Should not cause issues

        assert monitor_service.is_running is True

    def test_stop_monitoring_when_not_running(self, monitor_service):
        """Test stopping monitoring when not running."""
        monitor_service.stop_monitoring()  # Should not cause issues

        assert monitor_service.is_running is False

    def test_monitor_service_with_custom_interval(self):
        """Test MonitorService with custom monitoring interval."""
        custom_interval = 30
        monitor_service = MonitorService(monitoring_interval=custom_interval)

        assert monitor_service.monitoring_interval == custom_interval

    def test_monitor_service_status_structure(self, monitor_service):
        """Test that status has the expected structure."""
        status = monitor_service.get_status()

        expected_keys = ["is_running", "last_check", "uptime"]
        for key in expected_keys:
            assert key in status

    def test_monitor_service_uptime_calculation(self, monitor_service):
        """Test uptime calculation."""
        monitor_service.start_monitoring()
        status = monitor_service.get_status()

        assert status["uptime"] >= 0  # Should be non-negative

    def test_monitor_service_multiple_start_stop(self, monitor_service):
        """Test multiple start/stop cycles."""
        # First cycle
        monitor_service.start_monitoring()
        assert monitor_service.is_running is True

        monitor_service.stop_monitoring()
        assert monitor_service.is_running is False

        # Second cycle
        monitor_service.start_monitoring()
        assert monitor_service.is_running is True

        monitor_service.stop_monitoring()
        assert monitor_service.is_running is False
