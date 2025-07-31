from typing import List, Optional

from django.db.models import Q
from asgiref.sync import sync_to_async

from library_manager.models import Album as DjangoAlbum
from library_manager.tasks import download_missing_albums_for_artist

from ..graphql_types.models import Album, MutationResult
from .base import BaseService


class AlbumService(BaseService[Album]):
    def __init__(self):
        self.model = DjangoAlbum

    async def get_by_id(self, id: str) -> Optional[Album]:
        try:
            django_album = await sync_to_async(self.model.objects.get)(spotify_gid=id)
            return self._to_graphql_type(django_album)
        except self.model.DoesNotExist:
            return None

    async def get_connection(
        self,
        first: int = 20,
        after: Optional[str] = None,
        artist_id: Optional[int] = None,
        downloaded: Optional[bool] = None,
        wanted: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> tuple[List[Album], bool, int]:
        def fetch_items():
            queryset = self.model.objects.all()

            # Apply filters
            if artist_id:
                queryset = queryset.filter(artist__id=artist_id)

            if downloaded is not None:
                queryset = queryset.filter(downloaded=downloaded)

            if wanted is not None:
                queryset = queryset.filter(wanted=wanted)

            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) | Q(spotify_gid__icontains=search)
                )

            # Apply cursor-based pagination
            if after:
                id_after = self.decode_cursor(after)
                queryset = queryset.filter(id__gt=id_after)

            # Get total count before slicing
            total_count = queryset.count()

            # Get one extra item to determine if there are more pages
            items = list(queryset.order_by("id")[: first + 1])

            has_next_page = len(items) > first
            items = items[:first]  # Remove the extra item

            return (
                [self._to_graphql_type(item) for item in items],
                has_next_page,
                total_count,
            )

        return await sync_to_async(fetch_items)()

    async def update_album(
        self, album_id: str, is_wanted: Optional[bool] = None
    ) -> Album:
        django_album = await sync_to_async(self.model.objects.get)(spotify_gid=album_id)

        if is_wanted is not None:
            django_album.wanted = is_wanted
            await sync_to_async(django_album.save)()

            if is_wanted:
                # Queue download if marked as wanted
                pass
                # await sync_to_async(download_missing_albums_for_artist)(django_album.artist.id)

        return self._to_graphql_type(django_album)

    async def download_album(self, album_id: str) -> Album:
        django_album = await sync_to_async(self.model.objects.get)(spotify_gid=album_id)
        django_album.wanted = True
        await sync_to_async(django_album.save)()

        await sync_to_async(download_missing_albums_for_artist)(django_album.artist.id)
        return self._to_graphql_type(django_album)

    async def set_album_wanted(self, album_id: int, wanted: bool) -> MutationResult:
        def update_album():
            try:
                django_album = self.model.objects.select_related('artist').get(id=album_id)
                django_album.wanted = wanted
                django_album.save()
                return django_album
            except self.model.DoesNotExist:
                return None
            except Exception as e:
                raise e

        try:
            django_album = await sync_to_async(update_album)()
            
            if django_album is None:
                return MutationResult(
                    success=False,
                    message="Album not found",
                    album=None
                )

            return MutationResult(
                success=True,
                message="Album wanted status updated successfully",
                album=self._to_graphql_type(django_album)
            )
        except Exception as e:
            return MutationResult(
                success=False,
                message=f"Error updating album: {str(e)}",
                album=None
            )

    def _to_graphql_type(self, django_album: DjangoAlbum) -> Album:
        return Album(
            id=django_album.id,
            name=django_album.name,
            spotify_gid=django_album.spotify_gid,
            total_tracks=django_album.total_tracks,
            wanted=django_album.wanted,
            downloaded=django_album.downloaded,
            album_type=django_album.album_type,
            album_group=django_album.album_group,
            artist=django_album.artist.name if django_album.artist else None,
            artist_id=django_album.artist.id if django_album.artist else None,
        )
