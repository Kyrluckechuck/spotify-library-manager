"""
Integration tests for DownloaderService.

Tests the orchestration between DownloaderService and its dependencies
(AlbumService, ArtistService, PlaylistService) including URL parsing,
metadata fetching, and download routing.

These are integration tests because they test service interaction, not isolated units.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.graphql_types.models import MutationResult

# Mark all tests as integration tests
pytestmark = pytest.mark.integration


class TestDownloaderService:
    """Test DownloaderService URL parsing and routing."""

    @pytest.fixture
    def downloader_service(self):
        """Create a DownloaderService instance."""
        # Lazy import to avoid module-level service instantiation during worker fork
        from src.services.downloader import DownloaderService

        return DownloaderService()

    # ========================================================================
    # URL Normalization Tests
    # ========================================================================

    def test_normalize_spotify_url_from_web_url(self, downloader_service):
        """Test converting web URL to Spotify URI."""
        url = "https://open.spotify.com/track/13TJT0oh9TdIZxQJfVWSKb"
        normalized = downloader_service._normalize_spotify_url(url)
        assert normalized == "spotify:track:13TJT0oh9TdIZxQJfVWSKb"

    def test_normalize_spotify_url_already_uri(self, downloader_service):
        """Test that Spotify URIs are returned as-is."""
        url = "spotify:track:13TJT0oh9TdIZxQJfVWSKb"
        normalized = downloader_service._normalize_spotify_url(url)
        assert normalized == url

    def test_get_content_type_track(self, downloader_service):
        """Test identifying track URLs."""
        url = "spotify:track:13TJT0oh9TdIZxQJfVWSKb"
        content_type = downloader_service._get_content_type(url)
        assert content_type == "track"

    def test_get_content_type_album(self, downloader_service):
        """Test identifying album URLs."""
        url = "spotify:album:3dKJ6zmafq708xGTk94ibd"
        content_type = downloader_service._get_content_type(url)
        assert content_type == "album"

    def test_extract_id_from_uri(self, downloader_service):
        """Test extracting ID from Spotify URI."""
        url = "spotify:track:13TJT0oh9TdIZxQJfVWSKb"
        track_id = downloader_service._extract_id_from_url(url)
        assert track_id == "13TJT0oh9TdIZxQJfVWSKb"

    def test_extract_id_from_web_url(self, downloader_service):
        """Test extracting ID from web URL."""
        url = "https://open.spotify.com/track/13TJT0oh9TdIZxQJfVWSKb?si=abc123"
        track_id = downloader_service._extract_id_from_url(url)
        assert track_id == "13TJT0oh9TdIZxQJfVWSKb"

    # ========================================================================
    # Track Download Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_handle_track_download_queues_celery_task(self, downloader_service):
        """
        Test that track downloads queue a Celery task.

        The actual metadata fetching and album download happens in the worker,
        not in the web container. This test verifies the service correctly
        queues the download_single_track task.
        """
        track_url = "https://open.spotify.com/track/13TJT0oh9TdIZxQJfVWSKb"
        expected_track_id = "13TJT0oh9TdIZxQJfVWSKb"

        # Mock the task's delay method
        mock_delay = MagicMock()

        with patch("library_manager.tasks.download_single_track") as mock_task:
            mock_task.delay = mock_delay

            # Patch sync_to_async where it's imported
            def sync_to_async_passthrough(func):
                async def wrapper(*args, **kwargs):
                    return func(*args, **kwargs)

                return wrapper

            with patch(
                "asgiref.sync.sync_to_async", side_effect=sync_to_async_passthrough
            ):
                result = await downloader_service._handle_track_download(track_url)

                # Verify task was queued with the correct track ID
                mock_delay.assert_called_once_with(expected_track_id)

                # Verify success result
                assert result.success is True
                assert (
                    expected_track_id in result.message
                    or "track" in result.message.lower()
                )

    @pytest.mark.asyncio
    async def test_handle_track_download_with_track_name(self, downloader_service):
        """Test that track name is included in success message when provided."""
        track_url = "spotify:track:13TJT0oh9TdIZxQJfVWSKb"
        track_name = "Last Hurrah"

        mock_delay = MagicMock()

        with patch("library_manager.tasks.download_single_track") as mock_task:
            mock_task.delay = mock_delay

            def sync_to_async_passthrough(func):
                async def wrapper(*args, **kwargs):
                    return func(*args, **kwargs)

                return wrapper

            with patch(
                "asgiref.sync.sync_to_async", side_effect=sync_to_async_passthrough
            ):
                result = await downloader_service._handle_track_download(
                    track_url, track_name=track_name
                )

                assert result.success is True
                assert track_name in result.message

    @pytest.mark.asyncio
    async def test_handle_track_download_handles_task_queue_error(
        self, downloader_service
    ):
        """Test that errors during task queueing are handled gracefully."""
        track_url = "spotify:track:13TJT0oh9TdIZxQJfVWSKb"

        with patch("library_manager.tasks.download_single_track") as mock_task:
            mock_task.delay.side_effect = Exception("Celery broker connection failed")

            def sync_to_async_passthrough(func):
                async def wrapper(*args, **kwargs):
                    return func(*args, **kwargs)

                return wrapper

            with patch(
                "asgiref.sync.sync_to_async", side_effect=sync_to_async_passthrough
            ):
                result = await downloader_service._handle_track_download(track_url)

                assert result.success is False
                assert "failed to download track" in result.message.lower()

    # ========================================================================
    # Album Download Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_handle_album_download_routes_correctly(self, downloader_service):
        """Test that album URLs route to album service."""
        album_url = "https://open.spotify.com/album/3dKJ6zmafq708xGTk94ibd"
        expected_album_id = "3dKJ6zmafq708xGTk94ibd"

        mock_album = MagicMock()
        mock_album.name = "Test Album"

        with patch.object(
            downloader_service.album_service,
            "download_album",
            new_callable=AsyncMock,
            return_value=mock_album,
        ) as mock_download:
            result = await downloader_service._handle_album_download(album_url)

            mock_download.assert_called_once_with(expected_album_id)
            assert result.success is True

    # ========================================================================
    # Integration Test: download_url routing
    # ========================================================================

    @pytest.mark.asyncio
    async def test_download_url_routes_track_correctly(self, downloader_service):
        """Test that track URLs are correctly routed through download_url."""
        track_url = "https://open.spotify.com/track/13TJT0oh9TdIZxQJfVWSKb"

        mock_result = MutationResult(success=True, message="Track downloaded")

        # Mock validation to return valid
        mock_validation = MagicMock()
        mock_validation.valid = True
        mock_validation.resource_name = "Test Track"

        with (
            patch(
                "src.services.downloader.validate_spotify_resource_async",
                new_callable=AsyncMock,
                return_value=mock_validation,
            ),
            patch.object(
                downloader_service,
                "_handle_track_download",
                new_callable=AsyncMock,
                return_value=mock_result,
            ) as mock_handle,
        ):
            result = await downloader_service.download_url(track_url)

            mock_handle.assert_called_once()
            assert result.success is True

    @pytest.mark.asyncio
    async def test_download_url_returns_error_for_invalid_resource(
        self, downloader_service
    ):
        """Test that invalid Spotify resources return an error before queueing."""
        track_url = "https://open.spotify.com/track/invalidtrackid123"

        # Mock validation to return invalid (track not found)
        mock_validation = MagicMock()
        mock_validation.valid = False
        mock_validation.error_message = "Track not found on Spotify"

        with patch(
            "src.services.downloader.validate_spotify_resource_async",
            new_callable=AsyncMock,
            return_value=mock_validation,
        ):
            result = await downloader_service.download_url(track_url)

            assert result.success is False
            assert "not found" in result.message.lower()
