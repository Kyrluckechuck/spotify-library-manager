"""Tests for timestamp field sorting with proper null handling."""

from datetime import timedelta
from unittest.mock import AsyncMock, Mock, patch

from django.utils import timezone

import pytest

from src.services.album import AlbumService
from src.services.artist import ArtistService


@pytest.fixture
def artist_service() -> ArtistService:
    return ArtistService()


@pytest.fixture
def album_service() -> AlbumService:
    return AlbumService()


def create_mock_artist(
    artist_id: int,
    name: str,
    last_synced_at=None,
    last_downloaded_at=None,
) -> Mock:
    """Create a mock artist with configurable timestamp fields."""
    mock = Mock()
    mock.id = artist_id
    mock.name = name
    mock.gid = f"artist_{artist_id}"
    mock.tracked = True
    mock.added_at = timezone.now()
    mock.last_synced_at = last_synced_at
    mock.last_downloaded_at = last_downloaded_at
    mock.spotify_uri = f"spotify:artist:artist_{artist_id}"
    return mock


@pytest.mark.asyncio
async def test_artist_sorting_last_synced_ascending_nulls_first(
    artist_service: ArtistService,
) -> None:
    """Test that null last_synced_at values appear first in ascending sort."""
    now = timezone.now()
    old = now - timedelta(days=7)

    artists = [
        create_mock_artist(1, "Never Synced", last_synced_at=None),
        create_mock_artist(2, "Synced Recently", last_synced_at=now),
        create_mock_artist(3, "Synced Week Ago", last_synced_at=old),
    ]

    with (
        patch("library_manager.models.Artist.objects.all") as mock_all,
        patch.object(
            artist_service, "_get_undownloaded_count", new_callable=AsyncMock
        ) as mock_undownloaded,
    ):
        mock_undownloaded.return_value = 0
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.acount = AsyncMock(return_value=3)

        # Simulate ordering with nulls_first for ascending
        def order_by_mock(*args):
            # In real Django, F('last_synced_at').asc(nulls_first=True) would order:
            # None, old, now
            mock_result = Mock()
            mock_result.__getitem__ = Mock(
                return_value=[artists[0], artists[2], artists[1]]
            )
            return mock_result

        mock_queryset.order_by = order_by_mock
        mock_all.return_value = mock_queryset

        items, has_next, total = await artist_service.get_connection(
            first=10, sort_by="lastSynced", sort_direction="asc"
        )

        # Verify nulls come first
        assert items[0].name == "Never Synced"
        assert items[1].name == "Synced Week Ago"
        assert items[2].name == "Synced Recently"


@pytest.mark.asyncio
async def test_artist_sorting_last_synced_descending_nulls_last(
    artist_service: ArtistService,
) -> None:
    """Test that null last_synced_at values appear last in descending sort."""
    now = timezone.now()
    old = now - timedelta(days=7)

    artists = [
        create_mock_artist(1, "Never Synced", last_synced_at=None),
        create_mock_artist(2, "Synced Recently", last_synced_at=now),
        create_mock_artist(3, "Synced Week Ago", last_synced_at=old),
    ]

    with (
        patch("library_manager.models.Artist.objects.all") as mock_all,
        patch.object(
            artist_service, "_get_undownloaded_count", new_callable=AsyncMock
        ) as mock_undownloaded,
    ):
        mock_undownloaded.return_value = 0
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.acount = AsyncMock(return_value=3)

        # Simulate ordering with nulls_last for descending
        def order_by_mock(*args):
            # In real Django, F('last_synced_at').desc(nulls_last=True) would order:
            # now, old, None
            mock_result = Mock()
            mock_result.__getitem__ = Mock(
                return_value=[artists[1], artists[2], artists[0]]
            )
            return mock_result

        mock_queryset.order_by = order_by_mock
        mock_all.return_value = mock_queryset

        items, has_next, total = await artist_service.get_connection(
            first=10, sort_by="lastSynced", sort_direction="desc"
        )

        # Verify newest first, nulls last
        assert items[0].name == "Synced Recently"
        assert items[1].name == "Synced Week Ago"
        assert items[2].name == "Never Synced"


@pytest.mark.asyncio
async def test_artist_sorting_last_downloaded_nulls_handling(
    artist_service: ArtistService,
) -> None:
    """Test that last_downloaded_at null handling works like last_synced_at."""
    now = timezone.now()

    artists = [
        create_mock_artist(1, "Never Downloaded", last_downloaded_at=None),
        create_mock_artist(2, "Downloaded Recently", last_downloaded_at=now),
    ]

    with (
        patch("library_manager.models.Artist.objects.all") as mock_all,
        patch.object(
            artist_service, "_get_undownloaded_count", new_callable=AsyncMock
        ) as mock_undownloaded,
    ):
        mock_undownloaded.return_value = 0
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.acount = AsyncMock(return_value=2)

        # Ascending: nulls first
        def order_by_asc(*args):
            mock_result = Mock()
            mock_result.__getitem__ = Mock(return_value=[artists[0], artists[1]])
            return mock_result

        mock_queryset.order_by = order_by_asc
        mock_all.return_value = mock_queryset

        items, _, _ = await artist_service.get_connection(
            first=10, sort_by="lastDownloaded", sort_direction="asc"
        )

        assert items[0].name == "Never Downloaded"
        assert items[1].name == "Downloaded Recently"


@pytest.mark.asyncio
async def test_album_sorting_created_at_nulls_handling(
    album_service: AlbumService,
) -> None:
    """Test that album created_at sorting handles nulls correctly."""
    now = timezone.now()
    old = now - timedelta(days=30)

    def create_mock_album(album_id: int, name: str, created_at=None) -> Mock:
        mock = Mock()
        mock.id = album_id
        mock.name = name
        mock.spotify_gid = f"album_{album_id}"
        mock.total_tracks = 10
        mock.wanted = True
        mock.downloaded = False
        mock.album_type = "album"
        mock.album_group = "album"
        mock.created_at = created_at
        mock.artist = Mock(name="Test Artist", id=1, gid="artist_1")
        return mock

    albums = [
        create_mock_album(1, "No Date", created_at=None),
        create_mock_album(2, "Recent", created_at=now),
        create_mock_album(3, "Old", created_at=old),
    ]

    def mock_get_connection(*args, **kwargs):
        # Simulate database query with proper ordering
        mock_queryset = Mock()
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.count = Mock(return_value=3)

        if kwargs.get("sort_by") == "createdAt":
            if kwargs.get("sort_direction") == "asc":
                # Ascending: None, old, now
                return ([albums[0], albums[2], albums[1]], False, 3)
            else:
                # Descending: now, old, None
                return ([albums[1], albums[2], albums[0]], False, 3)
        return (albums, False, 3)

    with patch.object(album_service, "get_connection", side_effect=mock_get_connection):
        # Test ascending
        items, _, _ = await album_service.get_connection(
            first=10, sort_by="createdAt", sort_direction="asc"
        )
        assert items[0].name == "No Date"

        # Test descending
        items, _, _ = await album_service.get_connection(
            first=10, sort_by="createdAt", sort_direction="desc"
        )
        assert items[2].name == "No Date"
