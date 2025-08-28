"""Unit tests for event bus service."""

from unittest.mock import Mock

import pytest

from src.services.event_bus import EventBus


@pytest.fixture
def event_bus():
    """Create a fresh event bus instance for each test."""
    EventBus.reset()
    return EventBus()


class TestEventBus:
    """Test EventBus functionality."""

    def test_event_bus_initialization(self, event_bus):
        """Test EventBus can be initialized."""
        assert event_bus is not None
        assert hasattr(event_bus, "subscribe")
        assert hasattr(event_bus, "unsubscribe")
        assert hasattr(event_bus, "publish")

    def test_subscribe_to_event(self, event_bus):
        """Test subscribing to an event."""
        mock_handler = Mock()

        event_bus.subscribe("test_event", mock_handler)

        assert "test_event" in event_bus._subscribers
        assert mock_handler in event_bus._subscribers["test_event"]

    def test_subscribe_multiple_handlers(self, event_bus):
        """Test subscribing multiple handlers to the same event."""
        mock_handler1 = Mock()
        mock_handler2 = Mock()

        event_bus.subscribe("test_event", mock_handler1)
        event_bus.subscribe("test_event", mock_handler2)

        assert len(event_bus._subscribers["test_event"]) == 2
        assert mock_handler1 in event_bus._subscribers["test_event"]
        assert mock_handler2 in event_bus._subscribers["test_event"]

    def test_unsubscribe_handler(self, event_bus):
        """Test unsubscribing a handler from an event."""
        mock_handler = Mock()

        event_bus.subscribe("test_event", mock_handler)
        event_bus.unsubscribe("test_event", mock_handler)

        assert "test_event" not in event_bus._subscribers

    def test_unsubscribe_nonexistent_handler(self, event_bus):
        """Test unsubscribing a handler that doesn't exist."""
        mock_handler = Mock()

        # Should not raise an exception
        event_bus.unsubscribe("test_event", mock_handler)

        assert "test_event" not in event_bus._subscribers

    @pytest.mark.asyncio
    async def test_publish_event_with_handlers(self, event_bus):
        """Test publishing an event with handlers."""
        mock_handler = Mock()
        event_data = {"message": "test"}

        event_bus.subscribe("test_event", mock_handler)
        await event_bus.publish("test_event", event_data)

        mock_handler.assert_called_once_with(event_data)

    @pytest.mark.asyncio
    async def test_publish_event_without_handlers(self, event_bus):
        """Test publishing an event without handlers."""
        event_data = {"message": "test"}

        # Should not raise an exception
        await event_bus.publish("test_event", event_data)

    @pytest.mark.asyncio
    async def test_publish_event_multiple_handlers(self, event_bus):
        """Test publishing an event with multiple handlers."""
        mock_handler1 = Mock()
        mock_handler2 = Mock()
        event_data = {"message": "test"}

        event_bus.subscribe("test_event", mock_handler1)
        event_bus.subscribe("test_event", mock_handler2)
        await event_bus.publish("test_event", event_data)

        mock_handler1.assert_called_once_with(event_data)
        mock_handler2.assert_called_once_with(event_data)

    @pytest.mark.asyncio
    async def test_publish_event_handler_exception(self, event_bus):
        """Test publishing an event when handler raises an exception."""

        def failing_handler(data):
            raise Exception("Handler error")

        event_bus.subscribe("test_event", failing_handler)

        # Should not raise an exception
        await event_bus.publish("test_event", {"test": "data"})

    def test_subscribe_same_handler_twice(self, event_bus):
        """Test subscribing the same handler twice."""
        mock_handler = Mock()

        event_bus.subscribe("test_event", mock_handler)
        event_bus.subscribe("test_event", mock_handler)

        # Should only have one instance of the handler
        assert len(event_bus._subscribers["test_event"]) == 1

    @pytest.mark.asyncio
    async def test_publish_with_no_data(self, event_bus):
        """Test publishing an event with no data."""
        mock_handler = Mock()

        event_bus.subscribe("test_event", mock_handler)
        await event_bus.publish("test_event")

        mock_handler.assert_called_once_with(None)

    def test_event_bus_isolation(self):
        """Test that different event bus instances are isolated."""
        EventBus.reset()
        event_bus1 = EventBus()
        EventBus.reset()
        event_bus2 = EventBus()
        mock_handler = Mock()

        event_bus1.subscribe("test_event", mock_handler)

        assert "test_event" in event_bus1._subscribers
        assert "test_event" not in event_bus2._subscribers
