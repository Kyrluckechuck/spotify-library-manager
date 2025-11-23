"""Extended tests for album service to improve coverage."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from library_manager.models import Album as DjangoAlbum
from src.graphql_types.models import Album, MutationResult
from src.services.album import AlbumService


class TestAlbumServiceExtended:
    """Extended tests for AlbumService to improve coverage."""

    @pytest.fixture
    def album_service(self) -> AlbumService:
        """Create album service instance."""
        return AlbumService()

    @pytest.fixture
    def mock_django_album(self):
        """Create a mock Django album."""
        album = Mock(spec=DjangoAlbum)
        album.id = 1
        album.name = "Test Album"
        album.spotify_gid = "test_gid"
        album.total_tracks = 10
        album.wanted = True
        album.downloaded = False
        album.album_type = "album"
        album.album_group = "album"
        album.artist.name = "Test Artist"
        album.artist.id = 1
        return album

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, album_service, mock_django_album):
        """Test get_by_id when album is found."""
        with patch("src.services.album.sync_to_async") as mock_sync_to_async:
            # Mock the database query and _to_graphql_type conversion
            mock_get = AsyncMock(return_value=mock_django_album)
            mock_to_graphql = AsyncMock(
                return_value=Album(
                    id=1,
                    name="Test Album",
                    spotify_gid="test_gid",
                    total_tracks=10,
                    wanted=True,
                    downloaded=False,
                    album_type="album",
                    album_group="album",
                    artist="Test Artist",
                    artist_id=1,
                    artist_gid=None,
                )
            )
            mock_sync_to_async.side_effect = [mock_get, mock_to_graphql]

            result = await album_service.get_by_id("test_gid")

            assert result is not None
            assert isinstance(result, Album)
            assert result.name == "Test Album"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, album_service):
        """Test get_by_id when album is not found."""
        with patch("src.services.album.sync_to_async") as mock_sync_to_async:
            # Mock DoesNotExist exception
            mock_get = AsyncMock(side_effect=DjangoAlbum.DoesNotExist)
            mock_sync_to_async.return_value = mock_get

            result = await album_service.get_by_id("nonexistent")

            assert result is None

    @pytest.mark.asyncio
    async def test_update_album_with_database_id(
        self, album_service, mock_django_album
    ):
        """Test update_album with database ID format."""
        with patch("src.services.album.sync_to_async") as mock_sync_to_async:
            mock_get = AsyncMock(return_value=mock_django_album)
            mock_save = AsyncMock()
            mock_to_graphql = AsyncMock(
                return_value=Album(
                    id=1,
                    name="Test Album",
                    spotify_gid="test_gid",
                    total_tracks=10,
                    wanted=True,
                    downloaded=False,
                    album_type="album",
                    album_group="album",
                    artist="Test Artist",
                    artist_id=1,
                    artist_gid=None,
                )
            )
            mock_sync_to_async.side_effect = [mock_get, mock_save, mock_to_graphql]

            result = await album_service.update_album("123", is_wanted=True)

            assert isinstance(result, Album)

    @pytest.mark.asyncio
    async def test_update_album_with_spotify_gid(
        self, album_service, mock_django_album
    ):
        """Test update_album with Spotify GID format."""
        with patch("src.services.album.sync_to_async") as mock_sync_to_async:
            mock_get = AsyncMock(return_value=mock_django_album)
            mock_save = AsyncMock()
            mock_to_graphql = AsyncMock(
                return_value=Album(
                    id=1,
                    name="Test Album",
                    spotify_gid="test_gid",
                    total_tracks=10,
                    wanted=False,
                    downloaded=False,
                    album_type="album",
                    album_group="album",
                    artist="Test Artist",
                    artist_id=1,
                    artist_gid=None,
                )
            )
            mock_sync_to_async.side_effect = [mock_get, mock_save, mock_to_graphql]

            result = await album_service.update_album(
                "spotify_gid_123", is_wanted=False
            )

            assert isinstance(result, Album)

    @pytest.mark.asyncio
    async def test_update_album_value_error(self, album_service):
        """Test update_album with invalid ID raises ValueError."""
        with patch("src.services.album.sync_to_async") as mock_sync_to_async:
            mock_get = AsyncMock(side_effect=ValueError("Invalid ID"))
            mock_sync_to_async.return_value = mock_get

            with pytest.raises(ValueError, match="Invalid album ID format"):
                await album_service.update_album("invalid", is_wanted=True)

    @pytest.mark.asyncio
    async def test_update_album_does_not_exist(self, album_service):
        """Test update_album when album doesn't exist."""
        with patch("src.services.album.sync_to_async") as mock_sync_to_async:
            mock_get = AsyncMock(side_effect=DjangoAlbum.DoesNotExist)
            mock_sync_to_async.return_value = mock_get

            with pytest.raises(ValueError, match="Album with ID .* not found"):
                await album_service.update_album("123", is_wanted=True)

    @pytest.mark.asyncio
    async def test_download_album_with_database_id(
        self, album_service, mock_django_album
    ):
        """Test download_album with database ID."""
        with (
            patch("src.services.album.sync_to_async") as mock_sync_to_async,
            patch("library_manager.tasks.download_single_album") as mock_download_task,
        ):
            mock_download_task.delay = Mock()

            mock_get = AsyncMock(return_value=mock_django_album)
            mock_queue_task = AsyncMock()
            mock_to_graphql = AsyncMock(
                return_value=Album(
                    id=1,
                    name="Test Album",
                    spotify_gid="test_gid",
                    total_tracks=10,
                    wanted=True,
                    downloaded=False,
                    album_type="album",
                    album_group="album",
                    artist="Test Artist",
                    artist_id=1,
                    artist_gid=None,
                )
            )
            # Note: mock_save is not included because album.wanted is already True,
            # so the save operation in download_album is skipped
            mock_sync_to_async.side_effect = [
                mock_get,
                mock_queue_task,
                mock_to_graphql,
            ]

            result = await album_service.download_album("123")

            assert isinstance(result, Album)
            # Verify album was marked as wanted
            assert mock_django_album.wanted is True

    @pytest.mark.asyncio
    async def test_set_album_wanted_not_found(self, album_service):
        """Test set_album_wanted when album doesn't exist."""
        with patch("src.services.album.sync_to_async") as mock_sync_to_async:
            mock_get = AsyncMock(side_effect=DjangoAlbum.DoesNotExist)
            mock_sync_to_async.return_value = mock_get

            result = await album_service.set_album_wanted(123, True)

            assert isinstance(result, MutationResult)
            assert result.success is False
            assert "Album not found" in result.message
            assert result.album is None

    @pytest.mark.asyncio
    async def test_set_album_wanted_success(self, album_service, mock_django_album):
        """Test set_album_wanted successful operation."""
        with patch("src.services.album.sync_to_async") as mock_sync_to_async:
            mock_get = AsyncMock(return_value=mock_django_album)
            mock_save = AsyncMock()
            mock_to_graphql = AsyncMock(
                return_value=Album(
                    id=1,
                    name="Test Album",
                    spotify_gid="test_gid",
                    total_tracks=10,
                    wanted=True,
                    downloaded=False,
                    album_type="album",
                    album_group="album",
                    artist="Test Artist",
                    artist_id=1,
                    artist_gid=None,
                )
            )
            mock_sync_to_async.side_effect = [mock_get, mock_save, mock_to_graphql]

            result = await album_service.set_album_wanted(123, True)

            assert isinstance(result, MutationResult)
            assert result.success is True
            assert "successfully" in result.message
            assert result.album is not None

    @pytest.mark.asyncio
    async def test_set_album_wanted_save_error(self, album_service, mock_django_album):
        """Test set_album_wanted when save fails."""
        with patch("src.services.album.sync_to_async") as mock_sync_to_async:
            mock_get = AsyncMock(return_value=mock_django_album)
            mock_save = AsyncMock(side_effect=Exception("Save failed"))
            mock_sync_to_async.side_effect = [mock_get, mock_save]

            result = await album_service.set_album_wanted(123, True)

            assert isinstance(result, MutationResult)
            assert result.success is False
            assert "Error updating album" in result.message
            assert result.album is None

    def test_to_graphql_type_conversion(self, album_service, mock_django_album):
        """Test _to_graphql_type conversion."""
        result = album_service._to_graphql_type(mock_django_album)

        assert isinstance(result, Album)
        assert result.id == 1
        assert result.name == "Test Album"
        assert result.spotify_gid == "test_gid"
        assert result.total_tracks == 10
        assert result.wanted is True
        assert result.downloaded is False

    def test_to_graphql_type_with_invalid_id(self, album_service, mock_django_album):
        """Test _to_graphql_type with invalid ID handling."""
        mock_django_album.id = None  # Invalid ID

        result = album_service._to_graphql_type(mock_django_album)

        assert result.id == 0  # Should default to 0
