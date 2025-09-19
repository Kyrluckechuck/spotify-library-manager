"""Integration tests for SpotdlWrapper that catch real async/runtime issues."""

import asyncio
import threading
from unittest.mock import Mock, patch

import pytest
from downloader.spotdl_wrapper import SpotdlWrapper
from lib.config_class import Config

# Mark all tests in this module to not use the database
pytestmark = pytest.mark.django_db(transaction=False, databases=[])


class TestSpotdlWrapperIntegration:
    """Integration tests for SpotdlWrapper focusing on real async/runtime issues."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock config for testing."""
        config = Mock(spec=Config)
        config.log_level = "DEBUG"
        config.cookies_location = None
        config.po_token = None
        return config

    def test_event_loop_creation_in_main_thread(self, mock_config):
        """Test that SpotdlWrapper creates event loop properly in main thread."""
        # This test runs in the main thread
        with patch("downloader.spotdl_wrapper.Spotdl") as mock_spotdl:
            SpotdlWrapper(mock_config)

            # Verify that an event loop was created and passed to Spotdl
            mock_spotdl.assert_called_once()
            call_args = mock_spotdl.call_args

            # Check that the loop argument was passed
            assert "loop" in call_args[1]
            loop = call_args[1]["loop"]
            assert isinstance(loop, asyncio.AbstractEventLoop)
            assert not loop.is_closed()

    def test_event_loop_creation_in_worker_thread(self, mock_config):
        """Test that SpotdlWrapper creates event loop properly in worker threads (like Celery)."""
        results = {}
        exception_occurred = {}

        def worker_thread_task():
            """Task to run in a separate thread (simulating Celery worker)."""
            try:
                with patch("downloader.spotdl_wrapper.Spotdl") as mock_spotdl:
                    SpotdlWrapper(mock_config)

                    # Verify that an event loop was created and passed to Spotdl
                    mock_spotdl.assert_called_once()
                    call_args = mock_spotdl.call_args

                    # Check that the loop argument was passed
                    assert "loop" in call_args[1]
                    loop = call_args[1]["loop"]
                    assert isinstance(loop, asyncio.AbstractEventLoop)
                    assert not loop.is_closed()

                    # Verify we can get the event loop in this thread
                    current_loop = asyncio.get_event_loop()
                    assert current_loop == loop

                    results["success"] = True
                    results["loop"] = loop
            except Exception as e:
                exception_occurred["exception"] = e
                results["success"] = False

        # Run the test in a separate thread
        thread = threading.Thread(target=worker_thread_task)
        thread.start()
        thread.join()

        # Check results
        if not results.get("success", False):
            if "exception" in exception_occurred:
                raise exception_occurred["exception"]
            else:
                pytest.fail("Worker thread task failed without exception")

        assert results["success"] is True
        assert "loop" in results

    def test_multiple_worker_threads_event_loops(self, mock_config):
        """Test that multiple worker threads each get their own event loops."""
        results = []
        threads = []

        def worker_task(worker_id):
            """Task for each worker thread."""
            try:
                with patch("downloader.spotdl_wrapper.Spotdl") as mock_spotdl:
                    SpotdlWrapper(mock_config)

                    call_args = mock_spotdl.call_args
                    loop = call_args[1]["loop"]

                    results.append(
                        {
                            "worker_id": worker_id,
                            "success": True,
                            "loop_id": id(loop),
                            "loop_closed": loop.is_closed(),
                        }
                    )
            except Exception as e:
                results.append(
                    {"worker_id": worker_id, "success": False, "exception": str(e)}
                )

        # Create multiple worker threads
        for i in range(3):
            thread = threading.Thread(target=worker_task, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify results
        assert len(results) == 3
        successful_results = [r for r in results if r["success"]]
        assert len(successful_results) == 3

        # Each worker should have its own event loop
        loop_ids = [r["loop_id"] for r in successful_results]
        assert len(set(loop_ids)) == 3  # All loop IDs should be unique

        # All loops should be open
        for result in successful_results:
            assert not result["loop_closed"]

    @patch("downloader.spotdl_wrapper.Spotdl")
    def test_event_loop_reuse_when_valid(self, mock_spotdl, mock_config):
        """Test that existing valid event loops are reused."""
        # Create and set an event loop
        existing_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(existing_loop)

        try:
            SpotdlWrapper(mock_config)

            # Verify the existing loop was reused
            call_args = mock_spotdl.call_args
            passed_loop = call_args[1]["loop"]
            assert passed_loop == existing_loop

        finally:
            # Clean up
            existing_loop.close()

    @patch("downloader.spotdl_wrapper.Spotdl")
    def test_event_loop_replacement_when_closed(self, mock_spotdl, mock_config):
        """Test that closed event loops are replaced with new ones."""
        # Create and close an event loop
        closed_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(closed_loop)
        closed_loop.close()

        SpotdlWrapper(mock_config)

        # Verify a new loop was created
        call_args = mock_spotdl.call_args
        passed_loop = call_args[1]["loop"]
        assert passed_loop != closed_loop
        assert not passed_loop.is_closed()

        # Clean up
        passed_loop.close()
