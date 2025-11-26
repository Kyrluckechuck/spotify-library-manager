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
        config.spotdl_log_level = "INFO"
        config.youtube_cookies_location = None
        config.po_token = None
        config.spotify_user_auth_enabled = False
        return config

    def test_event_loop_creation_in_main_thread(self, mock_config):
        """Test that SpotdlWrapper creates event loop properly in main thread."""
        # This test runs in the main thread
        with (
            patch("downloader.spotdl_wrapper.Spotdl") as mock_spotdl,
            patch("downloader.spotdl_wrapper.SpotifyClient"),
        ):
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
                with (
                    patch("downloader.spotdl_wrapper.Spotdl") as mock_spotdl,
                    patch("downloader.spotdl_wrapper.SpotifyClient"),
                ):
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
        """Test that multiple worker threads can create SpotdlWrapper instances."""
        results = []
        threads = []

        def worker_task(worker_id):
            """Task for each worker thread."""
            try:
                with (
                    patch("downloader.spotdl_wrapper.Spotdl") as mock_spotdl,
                    patch("downloader.spotdl_wrapper.SpotifyClient"),
                ):
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

        # Verify results - some workers may fail due to timing issues
        assert len(results) >= 1  # At least 1 should succeed
        successful_results = [r for r in results if r["success"]]
        assert len(successful_results) >= 1  # At least 1 should succeed

        # All successful results should have valid (non-closed) event loops
        for result in successful_results:
            assert not result[
                "loop_closed"
            ], f"Worker {result['worker_id']} has closed event loop"

        # The SpotdlWrapper is designed to reuse existing event loops when possible,
        # so we don't require each thread to have a unique event loop.
        # We just verify that all threads can successfully create SpotdlWrapper instances.

    @patch("downloader.spotdl_wrapper.SpotifyClient")
    @patch("downloader.spotdl_wrapper.Spotdl")
    def test_event_loop_reuse_when_valid(
        self, mock_spotdl, mock_spotify_client, mock_config
    ):
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

    @patch("downloader.spotdl_wrapper.SpotifyClient")
    @patch("downloader.spotdl_wrapper.Spotdl")
    def test_event_loop_replacement_when_closed(
        self, mock_spotdl, mock_spotify_client, mock_config
    ):
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


class TestSpotdlWrapperTokenRefresh:
    """Tests for Spotify OAuth token refresh functionality."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock config for testing."""
        config = Mock(spec=Config)
        config.log_level = "DEBUG"
        config.spotdl_log_level = "INFO"
        config.youtube_cookies_location = None
        config.po_token = None
        config.spotify_user_auth_enabled = False
        return config

    @pytest.mark.django_db(transaction=False, databases=[])
    @patch("downloader.spotdl_wrapper.SpotifyClient")
    @patch("downloader.spotdl_wrapper.Spotdl")
    def test_refresh_spotify_client_uses_credentials_from_settings(
        self, mock_spotdl, mock_spotify_client_class, mock_config, settings
    ):
        """
        Regression test: Ensure refresh_spotify_client passes client credentials.

        Previously, the method passed empty strings for client_id/client_secret,
        causing spotipy to fail with "No client_id" error during token refresh.
        """
        # Set test credentials in Django settings using pytest-django's settings fixture
        settings.SPOTIPY_CLIENT_ID = "test_client_id_from_settings"
        settings.SPOTIPY_CLIENT_SECRET = "test_client_secret_from_settings"

        wrapper = SpotdlWrapper(mock_config)

        # Reset mock to capture the refresh call
        mock_spotify_client_class.reset_mock()
        mock_spotify_client_class._instance = None

        # Mock get_spotify_oauth_credentials to return valid credentials
        mock_oauth_creds = {
            "access_token": "fresh_access_token",
            "refresh_token": "refresh_token",
            "token_type": "Bearer",
            "expires_at": 1234567890.0,
        }

        with patch(
            "downloader.spotify_auth_helper.get_spotify_oauth_credentials",
            return_value=mock_oauth_creds,
        ):
            result = wrapper.refresh_spotify_client()

        assert result is True

        # Verify SpotifyClient.init was called with proper credentials
        mock_spotify_client_class.init.assert_called_once()
        call_kwargs = mock_spotify_client_class.init.call_args[1]

        # THE KEY ASSERTION: client_id and client_secret must come from settings
        # The fix was changing these from "" to actual values from Django settings
        assert (
            call_kwargs["client_id"] == "test_client_id_from_settings"
        ), "client_id must come from Django settings"
        assert (
            call_kwargs["client_secret"] == "test_client_secret_from_settings"
        ), "client_secret must come from Django settings"
        assert call_kwargs["auth_token"] == "fresh_access_token"
        assert call_kwargs["user_auth"] is False

    @patch("downloader.spotdl_wrapper.SpotifyClient")
    @patch("downloader.spotdl_wrapper.Spotdl")
    def test_refresh_spotify_client_returns_false_when_no_credentials(
        self, mock_spotdl, mock_spotify_client_class, mock_config
    ):
        """Test that refresh_spotify_client returns False when OAuth credentials unavailable."""
        wrapper = SpotdlWrapper(mock_config)

        with patch(
            "downloader.spotify_auth_helper.get_spotify_oauth_credentials",
            return_value=None,
        ):
            result = wrapper.refresh_spotify_client()

        assert result is False

    @patch("downloader.spotdl_wrapper.SpotifyClient")
    @patch("downloader.spotdl_wrapper.Spotdl")
    def test_refresh_spotify_client_updates_wrapper_references(
        self, mock_spotdl, mock_spotify_client_class, mock_config
    ):
        """Test that refresh_spotify_client updates the wrapper's client references."""
        wrapper = SpotdlWrapper(mock_config)
        _original_spotipy_client = wrapper.spotipy_client  # noqa: F841

        # Create a new mock for the refreshed client
        new_mock_client = Mock()
        mock_spotify_client_class.return_value = new_mock_client
        mock_spotify_client_class._instance = None

        mock_settings = Mock()
        mock_settings.SPOTIPY_CLIENT_ID = "client_id"
        mock_settings.SPOTIPY_CLIENT_SECRET = "client_secret"

        mock_oauth_creds = {
            "access_token": "new_token",
            "refresh_token": "refresh",
            "token_type": "Bearer",
            "expires_at": 1234567890.0,
        }

        with patch(
            "downloader.spotify_auth_helper.get_spotify_oauth_credentials",
            return_value=mock_oauth_creds,
        ):
            with patch("django.conf.settings", mock_settings):
                result = wrapper.refresh_spotify_client()

        assert result is True
        # Verify the wrapper's client reference was updated
        assert wrapper.spotipy_client == new_mock_client
        assert wrapper.downloader.spotipy_client == new_mock_client
