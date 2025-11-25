from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.graphql_types.models import Artist
from src.services.artist import ArtistService


@pytest.fixture
def artist_service() -> ArtistService:
    return ArtistService()


@pytest.fixture
def mock_django_artist() -> Mock:
    mock_artist = Mock()
    mock_artist.id = 1
    mock_artist.gid = "test_id"
    mock_artist.name = "Test Artist"
    mock_artist.tracked = True
    mock_artist.last_synced_at = datetime.now()
    mock_artist.last_downloaded_at = datetime.now()
    mock_artist.added_at = datetime.now()
    mock_artist.spotify_uri = "spotify:artist:test_id"
    return mock_artist


@pytest.mark.asyncio
async def test_get_by_id(
    artist_service: ArtistService, mock_django_artist: Mock
) -> None:
    with (
        patch(
            "library_manager.models.Artist.objects.aget", new_callable=AsyncMock
        ) as mock_aget,
        patch.object(
            artist_service, "_get_undownloaded_count", new_callable=AsyncMock
        ) as mock_undownloaded_count,
        patch.object(
            artist_service, "_get_album_count", new_callable=AsyncMock
        ) as mock_album_count,
        patch.object(
            artist_service, "_get_downloaded_album_count", new_callable=AsyncMock
        ) as mock_downloaded_album_count,
        patch.object(
            artist_service, "_get_song_count", new_callable=AsyncMock
        ) as mock_song_count,
    ):
        mock_aget.return_value = mock_django_artist
        mock_undownloaded_count.return_value = 5
        mock_album_count.return_value = 10
        mock_downloaded_album_count.return_value = 8
        mock_song_count.return_value = 50
        result = await artist_service.get_by_id("test_id")

        assert isinstance(result, Artist)
        assert result.id == 1
        assert result.name == "Test Artist"
        assert result.is_tracked is True
        assert result.album_count == 10
        assert result.downloaded_album_count == 8
        assert result.song_count == 50


@pytest.mark.asyncio
async def test_get_by_id_not_found(artist_service: ArtistService) -> None:
    with patch(
        "library_manager.models.Artist.objects.aget", new_callable=AsyncMock
    ) as mock_aget:
        mock_aget.side_effect = artist_service.model.DoesNotExist
        result = await artist_service.get_by_id("not_found")
        assert result is None


@pytest.mark.asyncio
async def test_get_connection(
    artist_service: ArtistService, mock_django_artist: Mock
) -> None:
    with (
        patch("library_manager.models.Artist.objects.all") as mock_all,
        patch.object(
            artist_service, "_get_undownloaded_count", new_callable=AsyncMock
        ) as mock_undownloaded_count,
    ):
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.count = Mock(return_value=1)
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__getitem__ = Mock(return_value=[mock_django_artist])

        mock_all.return_value = mock_queryset
        mock_undownloaded_count.return_value = 3

        items, has_next, total = await artist_service.get_connection(
            first=10, is_tracked=True
        )

        assert len(items) == 1
        assert isinstance(items[0], Artist)
        assert not has_next
        assert total == 1


@pytest.mark.asyncio
async def test_to_graphql_type_includes_timestamp_fields(
    artist_service: ArtistService, mock_django_artist: Mock
) -> None:
    """Test that GraphQL type conversion includes both timestamp fields."""
    with patch.object(
        artist_service, "_get_undownloaded_count", new_callable=AsyncMock
    ) as mock_count:
        mock_count.return_value = 0

        result = await artist_service._to_graphql_type_async(mock_django_artist)

        assert isinstance(result, Artist)
        # Verify both timestamp fields are present
        assert result.last_synced is not None
        assert result.last_downloaded is not None
        assert isinstance(result.last_synced, str)  # ISO format
        assert isinstance(result.last_downloaded, str)  # ISO format


@pytest.mark.asyncio
async def test_to_graphql_type_handles_null_timestamps(
    artist_service: ArtistService,
) -> None:
    """Test that null timestamps are handled correctly."""
    mock_artist = Mock()
    mock_artist.id = 1
    mock_artist.gid = "test_id"
    mock_artist.name = "Never Synced Artist"
    mock_artist.tracked = False
    mock_artist.last_synced_at = None  # Never synced
    mock_artist.last_downloaded_at = None  # Never downloaded
    mock_artist.added_at = datetime.now()
    mock_artist.spotify_uri = "spotify:artist:test_id"

    with patch.object(
        artist_service, "_get_undownloaded_count", new_callable=AsyncMock
    ) as mock_count:
        mock_count.return_value = 10

        result = await artist_service._to_graphql_type_async(mock_artist)

        assert isinstance(result, Artist)
        assert result.last_synced is None
        assert result.last_downloaded is None
