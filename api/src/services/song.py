"""Song service.

Note: Strawberry runtime-decorated types trigger attr-defined false-positives in MyPy
when instantiated. We disable that check for this module to avoid noisy errors.
"""

# mypy: disable-error-code=attr-defined
from typing import List, Optional, Tuple

from django.db.models import Q

from asgiref.sync import sync_to_async

from library_manager.models import Song as DjangoSong

from ..graphql_types.models import Song
from .base import BaseService


class SongService(BaseService[Song]):
    def __init__(self) -> None:
        super().__init__()
        self.model = DjangoSong

    async def get_connection(
        self,
        first: int = 20,
        after: Optional[str] = None,
        **filters: Optional[object],
    ) -> Tuple[List[Song], bool, int]:
        """Get paginated songs with filtering."""
        # Extract supported filters
        artist_id = (
            filters.get("artist_id")
            if isinstance(filters.get("artist_id"), int)
            else None
        )
        downloaded = (
            filters.get("downloaded")
            if isinstance(filters.get("downloaded"), bool)
            else None
        )
        unavailable = (
            filters.get("unavailable")
            if isinstance(filters.get("unavailable"), bool)
            else None
        )
        search = (
            filters.get("search") if isinstance(filters.get("search"), str) else None
        )
        sort_by = (
            filters.get("sort_by") if isinstance(filters.get("sort_by"), str) else None
        )
        sort_direction = (
            filters.get("sort_direction")
            if isinstance(filters.get("sort_direction"), str)
            else None
        )

        # Copy the exact pattern from ArtistService
        queryset = self.model.objects.all()

        # Apply filters
        if artist_id is not None:
            queryset = queryset.filter(primary_artist_id=artist_id)

        if downloaded is not None:
            queryset = queryset.filter(downloaded=downloaded)

        if unavailable is not None:
            queryset = queryset.filter(unavailable=unavailable)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(primary_artist__name__icontains=search)
            )

        # Apply sorting
        sort_field_map: dict[str, str] = {
            "name": "name",
            "primaryArtist": "primary_artist__name",
            "createdAt": "created_at",
            "downloaded": "downloaded",
        }

        order_field = "id"  # default
        if isinstance(sort_by, str):
            mapped_field = sort_field_map.get(sort_by)
            if mapped_field is not None:
                order_field = mapped_field
                if sort_direction == "desc":
                    order_field = f"-{order_field}"

        total_count = await sync_to_async(queryset.count)()

        # Apply cursor-based pagination
        if after:
            id_after = self.decode_cursor(after)
            queryset = queryset.filter(id__gt=id_after)

        # Get one extra item to determine if there are more pages
        def fetch_items() -> List[DjangoSong]:
            return list(queryset.order_by(order_field, "id")[: first + 1])

        items: List[DjangoSong] = await sync_to_async(fetch_items)()

        has_next_page = len(items) > first
        items = items[:first]  # Remove the extra item

        # Convert items to GraphQL types
        graphql_items = []
        for item in items:
            graphql_item = await self._to_graphql_type(item)
            graphql_items.append(graphql_item)

        return (
            graphql_items,
            has_next_page,
            total_count,
        )

    async def get_by_id(self, id: str) -> Optional[Song]:
        """Get a song by ID."""
        try:
            # Try to parse as database ID first (for internal operations)
            if id.isdigit():
                django_song = await self.model.objects.aget(id=int(id))
            else:
                # Fall back to gid for external API calls
                django_song = await self.model.objects.aget(gid=id)
            return await self._to_graphql_type(django_song)
        except ValueError:
            return None
        except self.model.DoesNotExist:
            return None

    async def get_by_gid(self, gid: str) -> Optional[Song]:
        """Get a song by Spotify GID."""
        try:
            django_song = await self.model.objects.aget(gid=gid)
            return await self._to_graphql_type(django_song)
        except self.model.DoesNotExist:
            return None

    async def _to_graphql_type(self, django_song: DjangoSong) -> Song:
        """Convert Django model to GraphQL type."""
        # Use sync_to_async for accessing related fields
        primary_artist_name = await sync_to_async(
            lambda: django_song.primary_artist.name
        )()
        primary_artist_id = await sync_to_async(lambda: django_song.primary_artist.id)()
        primary_artist_gid = await sync_to_async(
            lambda: django_song.primary_artist.gid
        )()

        # Use sync_to_async for file_path property which accesses file_path_ref
        file_path = await sync_to_async(lambda: django_song.file_path)()

        return Song(
            id=int(django_song.id),
            name=django_song.name,
            gid=django_song.gid,
            primary_artist=primary_artist_name,
            primary_artist_id=primary_artist_id,
            primary_artist_gid=primary_artist_gid,
            created_at=django_song.created_at.isoformat(),
            failed_count=django_song.failed_count,
            bitrate=django_song.bitrate,
            unavailable=django_song.unavailable,
            file_path=file_path,
            downloaded=django_song.downloaded,
            spotify_uri=django_song.spotify_uri,
        )
