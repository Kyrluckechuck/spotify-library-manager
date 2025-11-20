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
    # Track Download Tests (Regression test for bug fix)
    # ========================================================================

    @pytest.mark.asyncio
    async def test_handle_track_download_fetches_metadata_and_album_id(
        self, downloader_service
    ):
        """
        Test that track downloads:
        1. Fetch track metadata from /v1/tracks/{id} (NOT /v1/albums/{id})
        2. Extract album ID from track metadata
        3. Download the correct album

        This is a regression test for the bug where track IDs were incorrectly
        passed to download_album(), causing 404 errors.
        """
        track_url = "https://open.spotify.com/track/13TJT0oh9TdIZxQJfVWSKb"
        expected_track_id = "13TJT0oh9TdIZxQJfVWSKb"
        expected_album_id = "3dKJ6zmafq708xGTk94ibd"

        # Mock track metadata from Spotify
        mock_track_data = {
            "id": expected_track_id,
            "name": "Last Hurrah",
            "artists": [{"name": "Folded Dragons"}],
            "album": {
                "id": expected_album_id,
                "name": "Last Hurrah",
            },
            "external_ids": {"isrc": "USZUD1952123"},
            "duration_ms": 151000,
        }

        # Mock album object returned from download_album
        mock_album = MagicMock()
        mock_album.name = "Last Hurrah"
        mock_album.id = expected_album_id

        with (
            patch("asgiref.sync.sync_to_async") as mock_sync_to_async,
            patch.object(
                downloader_service.album_service,
                "download_album",
                new_callable=AsyncMock,
                return_value=mock_album,
            ) as mock_download_album,
        ):
            # Mock sync_to_async to wrap the function and make it callable
            def fake_sync_to_async(func):
                async def wrapper():
                    return func()

                return wrapper

            mock_sync_to_async.side_effect = fake_sync_to_async

            # Mock the downloader.get_track() call
            with (
                patch("downloader.downloader.Downloader") as mock_downloader_class,
                patch("spotdl.utils.spotify.SpotifyClient"),
            ):
                mock_downloader = MagicMock()
                mock_downloader.get_track.return_value = mock_track_data
                mock_downloader_class.return_value = mock_downloader

                result = await downloader_service._handle_track_download(track_url)

                # Verify track metadata was fetched (not album metadata)
                mock_downloader.get_track.assert_called_once_with(expected_track_id)

                # Verify album was downloaded with ALBUM ID, not TRACK ID
                mock_download_album.assert_called_once_with(expected_album_id)

                # Verify success result
                assert result.success is True
                assert "Last Hurrah" in result.message
                assert result.album == mock_album

    @pytest.mark.asyncio
    async def test_handle_track_download_track_without_album_fails(
        self, downloader_service
    ):
        """Test that tracks without album metadata raise an error."""
        track_url = "https://open.spotify.com/track/13TJT0oh9TdIZxQJfVWSKb"

        # Mock track data missing album info
        mock_track_data = {
            "id": "13TJT0oh9TdIZxQJfVWSKb",
            "name": "Orphan Track",
            # No album field!
        }

        with patch("asgiref.sync.sync_to_async") as mock_sync_to_async:

            def fake_sync_to_async(func):
                async def wrapper():
                    return func()

                return wrapper

            mock_sync_to_async.side_effect = fake_sync_to_async

            with (
                patch("downloader.downloader.Downloader") as mock_downloader_class,
                patch("spotdl.utils.spotify.SpotifyClient"),
            ):
                mock_downloader = MagicMock()
                mock_downloader.get_track.return_value = mock_track_data
                mock_downloader_class.return_value = mock_downloader

                result = await downloader_service._handle_track_download(track_url)

                assert result.success is False
                assert "no album data" in result.message.lower()

    @pytest.mark.asyncio
    async def test_handle_track_download_unavailable_track_with_metadata(
        self, downloader_service
    ):
        """
        Test that tracks unavailable for streaming but with metadata still work.

        This tests the scenario where:
        - Track is removed from Spotify streaming (unavailable in region)
        - But Spotify API still returns metadata (name, artist, ISRC, album ID)
        - System should successfully download from YouTube Music via album
        """
        track_url = "https://open.spotify.com/track/13TJT0oh9TdIZxQJfVWSKb"
        expected_album_id = "3dKJ6zmafq708xGTk94ibd"

        # Simulate track metadata available but not streamable
        # (available_markets is empty or restricted)
        mock_track_data = {
            "id": "13TJT0oh9TdIZxQJfVWSKb",
            "name": "Last Hurrah",
            "artists": [{"name": "Folded Dragons"}],
            "album": {
                "id": expected_album_id,
                "name": "Last Hurrah",
            },
            "external_ids": {"isrc": "USZUD1952123"},
            "is_playable": False,  # Not streamable
            "available_markets": [],  # Not available in any market
        }

        mock_album = MagicMock()
        mock_album.name = "Last Hurrah"
        mock_album.id = expected_album_id

        with (
            patch("asgiref.sync.sync_to_async") as mock_sync_to_async,
            patch.object(
                downloader_service.album_service,
                "download_album",
                new_callable=AsyncMock,
                return_value=mock_album,
            ) as mock_download_album,
        ):

            def fake_sync_to_async(func):
                async def wrapper():
                    return func()

                return wrapper

            mock_sync_to_async.side_effect = fake_sync_to_async

            with (
                patch("downloader.downloader.Downloader") as mock_downloader_class,
                patch("spotdl.utils.spotify.SpotifyClient"),
            ):
                mock_downloader = MagicMock()
                mock_downloader.get_track.return_value = mock_track_data
                mock_downloader_class.return_value = mock_downloader

                result = await downloader_service._handle_track_download(track_url)

                # Should succeed despite track being unavailable for streaming
                assert result.success is True
                assert "Last Hurrah" in result.message

                # Should download album (which will attempt YouTube Music download)
                mock_download_album.assert_called_once_with(expected_album_id)

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

        with patch.object(
            downloader_service,
            "_handle_track_download",
            new_callable=AsyncMock,
            return_value=mock_result,
        ) as mock_handle:
            result = await downloader_service.download_url(track_url)

            mock_handle.assert_called_once()
            assert result.success is True
