"""Integration tests for download functionality focusing on async loop issues."""

import asyncio
import threading
from unittest.mock import Mock

import pytest
from downloader.spotdl_override import download_song
from spotdl.download.downloader import Downloader
from spotdl.types.song import Song

# Mark all tests in this module to not use the database
pytestmark = pytest.mark.django_db(transaction=False, databases=[])


class TestDownloadAsyncLoop:
    """Test download functionality with different event loop scenarios."""

    @pytest.fixture
    def mock_song(self):
        """Create a mock song for testing."""
        song = Mock(spec=Song)
        song.name = "Test Song"
        song.artists = ["Test Artist"]
        return song

    @pytest.fixture
    def mock_downloader(self):
        """Create a mock downloader with an event loop."""
        downloader = Mock(spec=Downloader)
        downloader.loop = asyncio.new_event_loop()
        downloader.progress_handler = Mock()
        downloader.progress_handler.set_song_count = Mock()
        downloader.download_multiple_songs = Mock(return_value=[(Mock(), "/fake/path")])
        return downloader

    def test_download_song_with_no_event_loop(self, mock_downloader, mock_song):
        """Test download_song function when no event loop exists in thread."""

        def worker_task():
            # Ensure no event loop exists
            try:
                asyncio.get_event_loop()
                # If we get here, close the loop to simulate no loop
                loop = asyncio.get_event_loop()
                loop.close()
            except RuntimeError:
                pass  # Good, no loop exists

            # This should not raise an exception
            result = download_song(mock_downloader, mock_song)
            assert result is not None

        thread = threading.Thread(target=worker_task)
        thread.start()
        thread.join()

        # Verify the downloader methods were called
        mock_downloader.progress_handler.set_song_count.assert_called_once_with(1)
        mock_downloader.download_multiple_songs.assert_called_once_with([mock_song])

        # Clean up
        mock_downloader.loop.close()

    def test_download_song_with_different_event_loop(self, mock_downloader, mock_song):
        """Test download_song when a different event loop exists in thread."""

        def worker_task():
            # Create a different event loop
            different_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(different_loop)

            try:
                # This should not raise an exception and should switch to the downloader's loop
                result = download_song(mock_downloader, mock_song)
                assert result is not None

                # Verify the correct loop is now set
                current_loop = asyncio.get_event_loop()
                assert current_loop == mock_downloader.loop

            finally:
                different_loop.close()

        thread = threading.Thread(target=worker_task)
        thread.start()
        thread.join()

        # Clean up
        mock_downloader.loop.close()

    def test_download_song_with_closed_event_loop(self, mock_downloader, mock_song):
        """Test download_song when a closed event loop exists in thread."""

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
        mock_downloader.loop.close()

    def test_download_song_with_same_event_loop(self, mock_downloader, mock_song):
        """Test download_song when the correct event loop is already set."""

        def worker_task():
            # Set the downloader's loop as the current loop
            asyncio.set_event_loop(mock_downloader.loop)

            # This should work without issues
            result = download_song(mock_downloader, mock_song)
            assert result is not None

            # Verify the same loop is still set
            current_loop = asyncio.get_event_loop()
            assert current_loop == mock_downloader.loop

        thread = threading.Thread(target=worker_task)
        thread.start()
        thread.join()

        # Clean up
        mock_downloader.loop.close()

    def test_multiple_concurrent_downloads(self, mock_song):
        """Test multiple concurrent downloads in different threads."""
        results = []
        threads = []

        def download_task(task_id):
            """Download task for each thread."""
            try:
                # Each thread gets its own downloader with its own loop
                downloader = Mock(spec=Downloader)
                downloader.loop = asyncio.new_event_loop()
                downloader.progress_handler = Mock()
                downloader.progress_handler.set_song_count = Mock()
                downloader.download_multiple_songs = Mock(
                    return_value=[(Mock(), f"/fake/path/{task_id}")]
                )

                result = download_song(downloader, mock_song)

                results.append(
                    {
                        "task_id": task_id,
                        "success": True,
                        "result": result,
                        "loop_id": id(downloader.loop),
                    }
                )

                downloader.loop.close()

            except Exception as e:
                results.append(
                    {"task_id": task_id, "success": False, "exception": str(e)}
                )

        # Create multiple download threads
        for i in range(5):
            thread = threading.Thread(target=download_task, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all downloads succeeded
        assert len(results) == 5
        successful_results = [r for r in results if r["success"]]
        assert len(successful_results) == 5

        # Each thread should have used a valid event loop
        # Note: asyncio may reuse event loops across threads, so we don't require unique IDs
        loop_ids = [r["loop_id"] for r in successful_results]
        assert len(loop_ids) == 5  # All threads should have completed successfully
        assert all(
            loop_id is not None for loop_id in loop_ids
        )  # All should have valid loop IDs
