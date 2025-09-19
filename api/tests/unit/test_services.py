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
        with patch(
            "library_manager.models.Artist.objects.aget", new_callable=AsyncMock
        ) as mock_aget:
            mock_artist = Mock()
            mock_artist.gid = "test123"
            mock_artist.name = "Test Artist"
            mock_artist.tracked = True
            mock_artist.last_synced_at = datetime.now()
            mock_artist.id = 1  # Set the Django model ID
            mock_aget.return_value = mock_artist

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
        with patch("library_manager.models.Artist.objects.all") as mock_all:
            mock_queryset = Mock()
            mock_queryset.filter.return_value = mock_queryset
            mock_queryset.count = Mock(return_value=5)
            mock_queryset.order_by.return_value = mock_queryset

            # Return 4 items when first=3 to test has_next logic
            mock_artists = [
                Mock(gid=f"artist{i}", name=f"Artist {i}", tracked=True)
                for i in range(4)
            ]

            # Slicing returns a list directly which will be cast via list(...)
            mock_queryset.__getitem__ = Mock(return_value=mock_artists)
            mock_all.return_value = mock_queryset

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
            patch("asgiref.sync.sync_to_async") as mock_sync_to_async,
        ):

            # Configure mocks
            mock_get.return_value = mock_playlist
            mock_sync_to_async.side_effect = lambda func: AsyncMock(return_value=func())

            result = await playlist_service.update_playlist(
                playlist_id=1,
                name="Updated Name",
                url="https://open.spotify.com/playlist/updated",
                auto_track_artists=True,
            )

            # Verify the playlist was updated
            assert mock_playlist.name == "Updated Name"
            assert mock_playlist.url == "https://open.spotify.com/playlist/updated"
            assert mock_playlist.auto_track_artists is True
            assert result.success is True
            assert result.message == "Playlist updated successfully"


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
