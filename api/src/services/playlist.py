from typing import Optional, List, Any
from django.db.models import Q
from datetime import datetime

from src.library_manager.models import TrackedPlaylist as DjangoPlaylist
from src.library_manager.tasks import sync_tracked_playlist, sync_tracked_playlist_artists

from .base import BaseService
from ..types.models import Playlist

class PlaylistService(BaseService[Playlist]):
    def __init__(self):
        self.model = DjangoPlaylist

    async def get_by_id(self, id: str) -> Optional[Playlist]:
        try:
            django_playlist = await self.model.objects.aget(url__contains=id)
            return self._to_graphql_type(django_playlist)
        except self.model.DoesNotExist:
            return None

    async def get_connection(
        self,
        first: int = 20,
        after: Optional[str] = None,
        is_tracked: Optional[bool] = None,
        search: Optional[str] = None
    ) -> tuple[List[Playlist], bool, int]:
        queryset = self.model.objects.all()

        # Apply filters
        if is_tracked is not None:
            queryset = queryset.filter(enabled=is_tracked)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(url__icontains=search)
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

    async def track_playlist(
        self,
        playlist_id: str,
        auto_track_artists: bool = False
    ) -> Playlist:
        django_playlist = await self.model.objects.aget(url__contains=playlist_id)
        django_playlist.enabled = True
        django_playlist.auto_track_artists = auto_track_artists
        await django_playlist.asave()

        # Queue tasks
        sync_tracked_playlist(django_playlist)
        if auto_track_artists:
            sync_tracked_playlist_artists(django_playlist)

        return self._to_graphql_type(django_playlist)

    async def update_playlist(
        self,
        playlist_id: str,
        is_tracked: Optional[bool] = None,
        auto_track_artists: Optional[bool] = None
    ) -> Playlist:
        django_playlist = await self.model.objects.aget(url__contains=playlist_id)
        
        if is_tracked is not None:
            django_playlist.enabled = is_tracked
            
        if auto_track_artists is not None:
            django_playlist.auto_track_artists = auto_track_artists
            
        await django_playlist.asave()

        if is_tracked:
            sync_tracked_playlist(django_playlist)
        if auto_track_artists:
            sync_tracked_playlist_artists(django_playlist)

        return self._to_graphql_type(django_playlist)

    async def sync_playlist(self, playlist_id: str) -> Playlist:
        django_playlist = await self.model.objects.aget(url__contains=playlist_id)
        sync_tracked_playlist(django_playlist)
        return self._to_graphql_type(django_playlist)

    def _to_graphql_type(self, django_playlist: Any) -> Playlist:
        # Extract playlist ID from URL
        playlist_id = django_playlist.url.split('/')[-1]
        
        return Playlist(
            id=playlist_id,
            name=django_playlist.name,
            owner_id="",  # TODO: Add owner_id support to model
            spotify_url=django_playlist.url,
            image_url=None,  # TODO: Add image_url support
            track_count=0,  # TODO: Add track_count support
            is_tracked=django_playlist.enabled,
            auto_track_artists=django_playlist.auto_track_artists,
            last_synced=django_playlist.last_synced_at
        ) 