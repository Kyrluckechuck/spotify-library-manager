"""Unit tests for async event loop fixes in downloader."""

import asyncio
import threading
from unittest.mock import Mock

import pytest
from downloader.spotdl_override import download_song


class TestAsyncLoopFixes:
    """Test async event loop handling in download functionality."""

    @pytest.fixture
    def mock_downloader(self):
        """Create a mock downloader with an event loop."""
        downloader = Mock()
        downloader.loop = asyncio.new_event_loop()
        downloader.progress_handler = Mock()
        downloader.progress_handler.set_song_count = Mock()
        downloader.download_multiple_songs = Mock(return_value=[(Mock(), "/fake/path")])
        return downloader

    @pytest.fixture
    def mock_song(self):
        """Create a mock song for testing."""
        song = Mock()
        song.name = "Test Song"
        return song

    def test_download_song_sets_event_loop_when_none_exists(
        self, mock_downloader, mock_song
    ):
        """Test that download_song sets event loop when none exists in thread."""

        def worker_task():
            # Ensure no event loop exists in this thread
            try:
                current_loop = asyncio.get_event_loop()
                if not current_loop.is_closed():
                    current_loop.close()
            except RuntimeError:
                pass  # Good, no loop exists

            # Clear any event loop
            asyncio.set_event_loop(None)

            # This should not raise an exception
            result = download_song(mock_downloader, mock_song)
            assert result is not None

            # Verify the downloader's loop is now set
            current_loop = asyncio.get_event_loop()
            assert current_loop == mock_downloader.loop

        thread = threading.Thread(target=worker_task)
        thread.start()
        thread.join()

        # Verify mocks were called
        mock_downloader.progress_handler.set_song_count.assert_called_once_with(1)
        mock_downloader.download_multiple_songs.assert_called_once_with([mock_song])

        # Clean up
        if not mock_downloader.loop.is_closed():
            mock_downloader.loop.close()

    def test_download_song_replaces_closed_event_loop(self, mock_downloader, mock_song):
        """Test that download_song replaces a closed event loop."""

        def worker_task():
            # Create and close an event loop
            closed_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(closed_loop)
            closed_loop.close()

            # This should not raise an exception
            result = download_song(mock_downloader, mock_song)
            assert result is not None

            # Verify the correct loop is now set
            current_loop = asyncio.get_event_loop()
            assert current_loop == mock_downloader.loop
            assert not current_loop.is_closed()

        thread = threading.Thread(target=worker_task)
        thread.start()
        thread.join()

        # Clean up
        if not mock_downloader.loop.is_closed():
            mock_downloader.loop.close()

    def test_download_song_switches_to_correct_loop(self, mock_downloader, mock_song):
        """Test that download_song switches to the correct event loop."""

        def worker_task():
            # Create a different event loop
            different_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(different_loop)

            try:
                # This should not raise an exception
                result = download_song(mock_downloader, mock_song)
                assert result is not None

                # Verify the correct loop is now set
                current_loop = asyncio.get_event_loop()
                assert current_loop == mock_downloader.loop

            finally:
                if not different_loop.is_closed():
                    different_loop.close()

        thread = threading.Thread(target=worker_task)
        thread.start()
        thread.join()

        # Clean up
        if not mock_downloader.loop.is_closed():
            mock_downloader.loop.close()

    def test_download_song_preserves_correct_loop(self, mock_downloader, mock_song):
        """Test that download_song preserves the correct event loop when already set."""

        def worker_task():
            # Set the downloader's loop as the current loop
            asyncio.set_event_loop(mock_downloader.loop)

            # This should work without changing loops
            result = download_song(mock_downloader, mock_song)
            assert result is not None

            # Verify the same loop is still set
            current_loop = asyncio.get_event_loop()
            assert current_loop == mock_downloader.loop

        thread = threading.Thread(target=worker_task)
        thread.start()
        thread.join()

        # Clean up
        if not mock_downloader.loop.is_closed():
            mock_downloader.loop.close()

    def test_multiple_downloaders_in_threads(self, mock_song):
        """Test multiple downloaders each with their own event loops."""
        results = []
        threads = []
        # Keep references to loops to prevent GC and address reuse
        loops = []

        def download_task(task_id):
            """Download task for each thread."""
            try:
                # Each thread gets its own downloader with its own loop
                downloader = Mock()
                downloader.loop = asyncio.new_event_loop()
                loops.append(downloader.loop)  # Keep reference to prevent GC
                downloader.progress_handler = Mock()
                downloader.progress_handler.set_song_count = Mock()
                downloader.download_multiple_songs = Mock(
                    return_value=[(Mock(), f"/fake/path/{task_id}")]
                )

                result = download_song(downloader, mock_song)

                # Verify the correct loop was set
                current_loop = asyncio.get_event_loop()
                assert current_loop == downloader.loop

                results.append(
                    {
                        "task_id": task_id,
                        "success": True,
                        "result": result,
                        "loop_id": id(downloader.loop),
                    }
                )

            except Exception as e:
                results.append(
                    {"task_id": task_id, "success": False, "exception": str(e)}
                )

        # Create multiple download threads
        for i in range(3):
            thread = threading.Thread(target=download_task, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all downloads succeeded
        assert len(results) == 3
        successful_results = [r for r in results if r["success"]]
        assert len(successful_results) == 3

        # Each thread should have used a different event loop
        loop_ids = [r["loop_id"] for r in successful_results]
        assert len(set(loop_ids)) == 3  # All loop IDs should be unique

        # Clean up loops
        for loop in loops:
            if not loop.is_closed():
                loop.close()
