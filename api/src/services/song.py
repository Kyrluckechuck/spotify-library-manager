from typing import List, Optional, Tuple

from django.db.models import Q

from asgiref.sync import sync_to_async

from library_manager.models import Song as DjangoSong

from ..graphql_types.models import Song
from .base import BaseService


class SongService(BaseService):
    def __init__(self):
        super().__init__()
        self.model = DjangoSong

    async def get_connection(
        self,
        first: Optional[int] = 20,
        after: Optional[str] = None,
        artist_id: Optional[int] = None,
        downloaded: Optional[bool] = None,
        unavailable: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Song], bool, int]:
        """Get paginated songs with filtering."""
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

        # Apply cursor-based pagination
        if after:
            id_after = self.decode_cursor(after)
            queryset = queryset.filter(id__gt=id_after)

        # Get total count before slicing
        total_count = await sync_to_async(queryset.count)()

        # Get one extra item to determine if there are more pages
        items = await sync_to_async(list)(queryset.order_by("id")[: first + 1])

        has_next_page = len(items) > first
        items = items[:first]  # Remove the extra item

        return (
            [self._to_graphql_type(item) for item in items],
            has_next_page,
            total_count,
        )

    async def get_by_id(self, song_id: str) -> Optional[Song]:
        """Get a song by ID."""
        try:
            django_song = await self.model.objects.aget(id=song_id)
            return self._to_graphql_type(django_song)
        except self.model.DoesNotExist:
            return None

    async def get_by_gid(self, gid: str) -> Optional[Song]:
        """Get a song by Spotify GID."""
        try:
            django_song = await self.model.objects.aget(gid=gid)
            return self._to_graphql_type(django_song)
        except self.model.DoesNotExist:
            return None

    def _to_graphql_type(self, django_song: DjangoSong) -> Song:
        """Convert Django model to GraphQL type."""
        return Song(
            id=django_song.id,
            name=django_song.name,
            gid=django_song.gid,
            primary_artist=django_song.primary_artist.name,
            primary_artist_id=django_song.primary_artist.id,
            created_at=django_song.created_at,
            failed_count=django_song.failed_count,
            bitrate=django_song.bitrate,
            unavailable=django_song.unavailable,
            file_path=django_song.file_path,
            downloaded=django_song.downloaded,
            spotify_uri=django_song.spotify_uri,
        )
