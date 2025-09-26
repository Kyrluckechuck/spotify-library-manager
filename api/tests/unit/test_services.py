"""Unit tests for service layer."""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.services.album import AlbumService
from src.services.artist import ArtistService
from src.services.history import DownloadHistoryService
from src.services.playlist import PlaylistService


@pytest.mark.django_db
class TestArtistService:
    """Test cases for ArtistService."""

    @pytest.fixture
    def artist_service(self):
        return ArtistService()

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, artist_service):
        """Test successful artist retrieval by ID."""
        with (
            patch(
                "library_manager.models.Artist.objects.aget", new_callable=AsyncMock
            ) as mock_aget,
            patch.object(
                artist_service, "_get_undownloaded_count", new_callable=AsyncMock
            ) as mock_undownloaded_count,
        ):
            mock_artist = Mock()
            mock_artist.gid = "test123"
            mock_artist.name = "Test Artist"
            mock_artist.tracked = True
            mock_artist.last_synced_at = datetime.now()
            mock_artist.id = 1  # Set the Django model ID
            mock_artist.spotify_uri = "spotify:artist:test123"
            mock_aget.return_value = mock_artist
            mock_undownloaded_count.return_value = 5  # Mock undownloaded count

            result = await artist_service.get_by_id("test123")

            assert result is not None
            assert result.id == 1  # GraphQL type uses Django model ID
            assert result.name == "Test Artist"
            assert result.is_tracked is True

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, artist_service):
        """Test artist retrieval when not found."""
        with patch(
            "library_manager.models.Artist.objects.aget", new_callable=AsyncMock
        ) as mock_aget:
            mock_aget.side_effect = artist_service.model.DoesNotExist

            result = await artist_service.get_by_id("not_found")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_connection_with_filters(self, artist_service):
        """Test getting artist connection with filters."""
        with (
            patch("library_manager.models.Artist.objects.all") as mock_all,
            patch.object(
                artist_service, "_get_undownloaded_count", new_callable=AsyncMock
            ) as mock_undownloaded_count,
        ):
            mock_queryset = Mock()
            mock_queryset.filter.return_value = mock_queryset
            mock_queryset.count = Mock(return_value=5)
            mock_queryset.order_by.return_value = mock_queryset

            # Return 4 items when first=3 to test has_next logic
            mock_artists = []
            for i in range(4):
                mock_artist = Mock()
                mock_artist.gid = f"artist{i}"
                mock_artist.name = f"Artist {i}"
                mock_artist.tracked = True
                mock_artist.spotify_uri = f"spotify:artist:artist{i}"
                mock_artists.append(mock_artist)

            # Slicing returns a list directly which will be cast via list(...)
            mock_queryset.__getitem__ = Mock(return_value=mock_artists)
            mock_all.return_value = mock_queryset
            mock_undownloaded_count.return_value = (
                2  # Mock undownloaded count for each artist
            )

            items, has_next, total = await artist_service.get_connection(
                first=3, is_tracked=True, search="Artist"
            )

            assert len(items) == 3
            assert total == 5
            assert has_next is True


@pytest.mark.django_db
class TestAlbumService:
    """Test cases for AlbumService."""

    @pytest.fixture
    def album_service(self):
        return AlbumService()

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, album_service):
        """Test successful album retrieval by ID."""
        with patch("library_manager.models.Album.objects.get") as mock_get:
            mock_album = Mock()
            mock_album.spotify_gid = "album123"
            mock_album.name = "Test Album"
            mock_album.total_tracks = 10
            mock_album.wanted = True
            mock_album.downloaded = False
            mock_album.failed_count = 0
            mock_album.spotify_uri = "spotify:album:album123"
            mock_album.artist = Mock()
            mock_album.artist.gid = "artist123"
            mock_get.return_value = mock_album

            result = await album_service.get_by_id("album123")

            assert result is not None
            assert result.spotify_gid == "album123"
            assert result.name == "Test Album"
            assert result.total_tracks == 10
            assert result.wanted is True
            assert result.downloaded is False


@pytest.mark.django_db
class TestPlaylistService:
    """Test cases for PlaylistService."""

    @pytest.fixture
    def playlist_service(self):
        return PlaylistService()

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, playlist_service):
        """Test successful playlist retrieval by ID."""
        with patch(
            "library_manager.models.TrackedPlaylist.objects.get",
        ) as mock_get:
            mock_playlist = Mock()
            mock_playlist.id = 1
            mock_playlist.name = "Test Playlist"
            mock_playlist.url = "https://open.spotify.com/playlist/test123"
            mock_playlist.enabled = True
            mock_playlist.auto_track_artists = True
            mock_playlist.last_synced_at = None
            mock_get.return_value = mock_playlist

            result = await playlist_service.get_by_id("test123")

            assert result is not None
            assert result.id == 1
            assert result.name == "Test Playlist"
            assert result.url == "https://open.spotify.com/playlist/test123"
            assert result.auto_track_artists is True

    @pytest.mark.asyncio
    async def test_update_playlist_with_url(self, playlist_service):
        """Test updating playlist including URL."""
        # Mock the get operation
        mock_playlist = Mock()
        mock_playlist.id = 1
        mock_playlist.name = "Original Name"
        mock_playlist.url = "https://open.spotify.com/playlist/original"
        mock_playlist.auto_track_artists = False
        mock_playlist.save = Mock()

        with (
            patch("library_manager.models.TrackedPlaylist.objects.get") as mock_get,
            patch(
                "library_manager.models.TrackedPlaylist.objects.filter"
            ) as mock_filter,
            patch("asgiref.sync.sync_to_async") as mock_sync_to_async,
        ):

            # Configure mocks
            mock_get.return_value = mock_playlist
            # Mock the duplicate check filter to return no existing playlists
            mock_filter.return_value.exclude.return_value.first.return_value = None
            mock_sync_to_async.side_effect = lambda func: AsyncMock(return_value=func())

            result = await playlist_service.update_playlist(
                playlist_id=1,
                name="Updated Name",
                url="https://open.spotify.com/playlist/updated",
                auto_track_artists=True,
            )

            # Verify the playlist was updated
            assert mock_playlist.name == "Updated Name"
            assert (
                mock_playlist.url == "spotify:playlist:updated"
            )  # URL should be normalized
            assert mock_playlist.auto_track_artists is True
            assert result.success is True
            assert result.message == "Playlist updated successfully"

    @pytest.mark.asyncio
    async def test_create_playlist_deduplication(self, playlist_service):
        """Test that create_playlist handles URL deduplication correctly."""
        # Mock existing playlist with normalized URL
        mock_existing_playlist = Mock()
        mock_existing_playlist.id = 1
        mock_existing_playlist.name = "Existing Playlist"
        mock_existing_playlist.url = "spotify:playlist:12345"

        with (
            patch(
                "library_manager.models.TrackedPlaylist.objects.filter"
            ) as mock_filter,
            patch("asgiref.sync.sync_to_async") as mock_sync_to_async,
        ):
            # Configure mocks to return existing playlist
            mock_filter.return_value.first.return_value = mock_existing_playlist
            mock_sync_to_async.side_effect = lambda func: AsyncMock(return_value=func())

            result = await playlist_service.create_playlist(
                name="New Playlist",
                url="https://open.spotify.com/playlist/12345?si=tracking_param",
                auto_track_artists=False,
            )

            # Should return existing playlist, not create new one
            assert result.id == 1
            assert result.name == "Existing Playlist"
            # Verify URL was normalized for lookup
            mock_filter.assert_called_once_with(url="spotify:playlist:12345")

    @pytest.mark.asyncio
    async def test_update_playlist_duplicate_detection(self, playlist_service):
        """Test that update_playlist detects duplicates correctly."""
        # Mock the current playlist
        mock_current_playlist = Mock()
        mock_current_playlist.id = 1
        mock_current_playlist.url = "spotify:playlist:original"

        # Mock existing duplicate playlist
        mock_duplicate_playlist = Mock()
        mock_duplicate_playlist.id = 2
        mock_duplicate_playlist.name = "Existing Duplicate"

        with (
            patch("library_manager.models.TrackedPlaylist.objects.get") as mock_get,
            patch(
                "library_manager.models.TrackedPlaylist.objects.filter"
            ) as mock_filter,
            patch("asgiref.sync.sync_to_async") as mock_sync_to_async,
        ):
            # Configure mocks
            mock_get.return_value = mock_current_playlist
            mock_filter.return_value.exclude.return_value.first.return_value = (
                mock_duplicate_playlist
            )
            mock_sync_to_async.side_effect = lambda func: AsyncMock(return_value=func())

            result = await playlist_service.update_playlist(
                playlist_id=1,
                name="Updated Name",
                url="https://open.spotify.com/playlist/duplicate?si=param",
                auto_track_artists=False,
            )

            # Should fail due to duplicate
            assert result.success is False
            assert "already exists" in result.message
            assert "Existing Duplicate" in result.message

    def test_normalize_spotify_url(self, playlist_service):
        """Test URL normalization with various formats."""
        # Test web URL with tracking parameters
        url1 = (
            "https://open.spotify.com/playlist/12345?si=tracking_param&utm_source=web"
        )
        normalized1 = playlist_service._normalize_spotify_url(url1)
        assert normalized1 == "spotify:playlist:12345"

        # Test web URL without parameters
        url2 = "https://open.spotify.com/playlist/67890"
        normalized2 = playlist_service._normalize_spotify_url(url2)
        assert normalized2 == "spotify:playlist:67890"

        # Test already normalized URI
        url3 = "spotify:playlist:abcdef"
        normalized3 = playlist_service._normalize_spotify_url(url3)
        assert normalized3 == "spotify:playlist:abcdef"

        # Test other content types
        url4 = "https://open.spotify.com/artist/artist123?si=param"
        normalized4 = playlist_service._normalize_spotify_url(url4)
        assert normalized4 == "spotify:artist:artist123"

    @pytest.mark.asyncio
    async def test_create_playlist_detects_http_url_duplicates(self, playlist_service):
        """Test that create_playlist detects duplicates when existing playlist has HTTP URL."""
        # Mock existing playlist with HTTP URL (like existing data)
        mock_existing_playlist = Mock()
        mock_existing_playlist.id = 1
        mock_existing_playlist.name = "Existing HTTP Playlist"
        mock_existing_playlist.url = (
            "https://open.spotify.com/playlist/12345?si=old_param"
        )

        with (
            patch.object(
                playlist_service, "_find_duplicate_playlist"
            ) as mock_find_duplicate,
            patch("asgiref.sync.sync_to_async") as mock_sync_to_async,
        ):
            # Configure mock to return existing playlist
            mock_find_duplicate.return_value = mock_existing_playlist
            mock_sync_to_async.side_effect = lambda func: AsyncMock(return_value=func())

            result = await playlist_service.create_playlist(
                name="New Playlist",
                url="https://open.spotify.com/playlist/12345?si=new_param",
                auto_track_artists=False,
            )

            # Should return existing playlist
            assert result.id == 1
            assert result.name == "Existing HTTP Playlist"
            # Verify _find_duplicate_playlist was called with normalized URI
            mock_find_duplicate.assert_called_once_with("spotify:playlist:12345")

    def test_find_duplicate_playlist_cross_format_detection(self, playlist_service):
        """Test that _find_duplicate_playlist detects duplicates across HTTP/URI formats."""
        # Test with a normalized URI input, should find HTTP format existing playlist
        with (
            patch(
                "library_manager.models.TrackedPlaylist.objects.filter"
            ) as mock_filter,
        ):
            # Mock the QuerySet chain for exact match (returns None)
            mock_exact_queryset = Mock()
            mock_exact_queryset.first.return_value = None

            # Mock the QuerySet chain for HTTP format match (returns existing)
            mock_existing_playlist = Mock()
            mock_existing_playlist.id = 1
            mock_http_queryset = Mock()
            mock_http_queryset.first.return_value = mock_existing_playlist

            # Configure filter calls
            def filter_side_effect(*args, **kwargs):
                if "url" in kwargs:
                    return mock_exact_queryset
                else:
                    # This is the Q() filter for HTTP URLs
                    return mock_http_queryset

            mock_filter.side_effect = filter_side_effect

            result = playlist_service._find_duplicate_playlist("spotify:playlist:12345")

            assert result == mock_existing_playlist
            # Should have tried exact match first, then HTTP format
            assert mock_filter.call_count == 2


@pytest.mark.django_db
class TestDownloadHistoryService:
    """Test cases for DownloadHistoryService."""

    @pytest.fixture
    def history_service(self):
        return DownloadHistoryService()

    @pytest.mark.asyncio
    async def test_get_connection_with_pagination(self, history_service):
        """Test getting download history with pagination."""
        with patch("library_manager.models.DownloadHistory.objects.all") as mock_all:
            mock_queryset = Mock()
            mock_queryset.filter.return_value = mock_queryset
            mock_queryset.acount = AsyncMock(return_value=20)
            mock_queryset.order_by.return_value = mock_queryset

            # Create proper mock histories with attributes
            mock_histories = []
            for i in range(11):  # Return 11 items when first=10 to test has_next logic
                mock_history = Mock()
                mock_history.id = i
                mock_history.url = f"spotify:track:song{i}"
                mock_history.added_at = datetime.now()
                mock_history.completed_at = datetime.now() if i % 2 == 0 else None
                mock_history.progress = 100 if i % 2 == 0 else 0
                mock_histories.append(mock_history)

            # Mock the slicing behavior
            mock_slice = Mock()
            mock_slice.all = AsyncMock(return_value=mock_histories)
            mock_queryset.__getitem__ = Mock(return_value=mock_slice)
            mock_all.return_value = mock_queryset

            items, has_next, total = await history_service.get_connection(
                first=10, entity_type="SONG"
            )

            assert len(items) == 10
            assert total == 20
            assert has_next is True
