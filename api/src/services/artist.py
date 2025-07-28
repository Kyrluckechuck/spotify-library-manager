from typing import Optional, List
from django.db.models import Q

from library_manager.models import Artist as DjangoArtist
from library_manager.tasks import fetch_all_albums_for_artist, download_missing_albums_for_artist

from .base import BaseService
from ..types.models import Artist

class ArtistService(BaseService[Artist]):
    def __init__(self):
        self.model = DjangoArtist

    async def get_by_id(self, id: str) -> Optional[Artist]:
        try:
            django_artist = await self.model.objects.aget(gid=id)
            return self._to_graphql_type(django_artist)
        except self.model.DoesNotExist:
            return None

    async def get_connection(
        self,
        first: int = 20,
        after: Optional[str] = None,
        is_tracked: Optional[bool] = None,
        search: Optional[str] = None
    ) -> tuple[List[Artist], bool, int]:
        queryset = self.model.objects.all()

        # Apply filters
        if is_tracked is not None:
            queryset = queryset.filter(tracked=is_tracked)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(gid__icontains=search)
            )

        # Apply cursor-based pagination
        if after:
            id_after = self.decode_cursor(after)
            queryset = queryset.filter(id__gt=id_after)

        # Get total count before slicing
        total_count = await queryset.acount()

        # Get one extra item to determine if there are more pages
        items = await queryset.order_by('id')[:first + 1].all()
        
        has_next_page = len(items) > first
        items = items[:first]  # Remove the extra item

        return [self._to_graphql_type(item) for item in items], has_next_page, total_count

    async def track_artist(self, artist_id: str, auto_download: bool = False) -> Artist:
        django_artist = await self.model.objects.aget(gid=artist_id)
        django_artist.tracked = True
        await django_artist.asave()

        # Queue tasks
        fetch_all_albums_for_artist(django_artist.id)
        if auto_download:
            download_missing_albums_for_artist(django_artist.id)

        return self._to_graphql_type(django_artist)

    async def update_artist(
        self,
        artist_id: str,
        is_tracked: Optional[bool] = None,
        auto_download: Optional[bool] = None
    ) -> Artist:
        django_artist = await self.model.objects.aget(gid=artist_id)
        
        if is_tracked is not None:
            django_artist.tracked = is_tracked
            
        if auto_download and not django_artist.tracked:
            django_artist.tracked = True
            
        await django_artist.asave()

        if auto_download:
            download_missing_albums_for_artist(django_artist.id)

        return self._to_graphql_type(django_artist)

    async def sync_artist(self, artist_id: str) -> Artist:
        django_artist = await self.model.objects.aget(gid=artist_id)
        fetch_all_albums_for_artist(django_artist.id)
        return self._to_graphql_type(django_artist)

    def _to_graphql_type(self, django_artist: DjangoArtist) -> Artist:
        return Artist(
            id=django_artist.gid,
            name=django_artist.name,
            spotify_url=f"spotify:artist:{django_artist.gid}",
            image_url=None,  # TODO: Add image URL support
            is_tracked=django_artist.tracked,
            last_synced=django_artist.last_synced_at,
            auto_download=False  # TODO: Add auto_download support to model
        ) 