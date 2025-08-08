from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from api.src.graphql_types.models import Artist
from api.src.services.artist import ArtistService


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
    mock_artist.added_at = datetime.now()
    return mock_artist


@pytest.mark.asyncio
async def test_get_by_id(
    artist_service: ArtistService, mock_django_artist: Mock
) -> None:
    with patch(
        "library_manager.models.Artist.objects.aget", new_callable=AsyncMock
    ) as mock_aget:
        mock_aget.return_value = mock_django_artist
        result = await artist_service.get_by_id("test_id")

        assert isinstance(result, Artist)
        assert result.id == 1
        assert result.name == "Test Artist"
        assert result.is_tracked is True


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
    with patch("library_manager.models.Artist.objects.all") as mock_all:
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.count = Mock(return_value=1)
        mock_queryset.order_by.return_value = mock_queryset
        mock_queryset.__getitem__ = Mock(return_value=[mock_django_artist])

        mock_all.return_value = mock_queryset

        items, has_next, total = await artist_service.get_connection(
            first=10, is_tracked=True
        )

        assert len(items) == 1
        assert isinstance(items[0], Artist)
        assert not has_next
        assert total == 1
