from typing import Optional, List, Any
from django.db.models import Q

from library_manager.models import Album as DjangoAlbum
from library_manager.tasks import download_missing_albums_for_artist

from .base import BaseService
from ..types.models import Album, DownloadStatus

class AlbumService(BaseService[Album]):
    def __init__(self):
        self.model = DjangoAlbum

    async def get_by_id(self, id: str) -> Optional[Album]:
        try:
            django_album = await self.model.objects.aget(spotify_gid=id)
            return self._to_graphql_type(django_album)
        except self.model.DoesNotExist:
            return None

    async def get_connection(
        self,
        first: int = 20,
        after: Optional[str] = None,
        artist_id: Optional[str] = None,
        is_downloaded: Optional[bool] = None,
        is_wanted: Optional[bool] = None,
        search: Optional[str] = None
    ) -> tuple[List[Album], bool, int]:
        queryset = self.model.objects.all()

        # Apply filters
        if artist_id:
            queryset = queryset.filter(artist__gid=artist_id)
        
        if is_downloaded is not None:
            queryset = queryset.filter(downloaded=is_downloaded)
            
        if is_wanted is not None:
            queryset = queryset.filter(wanted=is_wanted)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(spotify_gid__icontains=search)
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

    async def update_album(
        self,
        album_id: str,
        is_wanted: Optional[bool] = None
    ) -> Album:
        django_album = await self.model.objects.aget(spotify_gid=album_id)
        
        if is_wanted is not None:
            django_album.wanted = is_wanted
            await django_album.asave()

            if is_wanted:
                # Queue download if marked as wanted
                download_missing_albums_for_artist(django_album.artist.id)

        return self._to_graphql_type(django_album)

    async def download_album(self, album_id: str) -> Album:
        django_album = await self.model.objects.aget(spotify_gid=album_id)
        django_album.wanted = True
        await django_album.asave()
        
        download_missing_albums_for_artist(django_album.artist.id)
        return self._to_graphql_type(django_album)

    def _to_graphql_type(self, django_album: Any) -> Album:
        status = None
        if django_album.downloaded:
            status = DownloadStatus.COMPLETED
        elif django_album.failed_count > 0:
            status = DownloadStatus.FAILED
        elif django_album.wanted:
            status = DownloadStatus.PENDING

        return Album(
            id=django_album.spotify_gid,
            name=django_album.name,
            artist_id=django_album.artist.gid,
            spotify_url=django_album.spotify_uri,
            release_date=None,  # TODO: Add release_date to model
            image_url=None,  # TODO: Add image_url to model
            is_downloaded=django_album.downloaded,
            is_wanted=django_album.wanted,
            download_status=status,
            track_count=django_album.total_tracks
        ) 