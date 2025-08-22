# mypy: disable-error-code=attr-defined
from typing import Any, List, Optional, Tuple

from django.db.models import Q

from asgiref.sync import sync_to_async

from library_manager.models import Album as DjangoAlbum
from library_manager.tasks import download_missing_albums_for_artist

from ..graphql_types.models import Album, MutationResult
from .base import BaseService


class AlbumService(BaseService[Album]):
    def __init__(self) -> None:
        super().__init__()
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
        **filters: Any,
    ) -> Tuple[List[Album], bool, int]:
        artist_id: Optional[int] = filters.get("artist_id")
        downloaded: Optional[bool] = filters.get("downloaded")
        wanted: Optional[bool] = filters.get("wanted")
        search: Optional[str] = filters.get("search")

        def fetch_items() -> Tuple[List[Album], bool, int]:
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
        try:
            # Try to parse as database ID first (for internal operations)
            if album_id.isdigit():
                django_album = await sync_to_async(self.model.objects.get)(
                    id=int(album_id)
                )
            else:
                # Fall back to spotify_gid for external API calls
                django_album = await sync_to_async(self.model.objects.get)(
                    spotify_gid=album_id
                )

            if is_wanted is not None:
                django_album.wanted = is_wanted
                await sync_to_async(django_album.save)()

                if is_wanted:
                    # Queue download if marked as wanted
                    pass
                    # await sync_to_async(download_missing_albums_for_artist)(django_album.artist.id)

            return self._to_graphql_type(django_album)
        except ValueError:
            raise ValueError(f"Invalid album ID format: {album_id}")
        except self.model.DoesNotExist:
            raise ValueError(f"Album with ID {album_id} not found")
        except Exception as e:
            raise Exception(f"Error updating album: {str(e)}")

    async def download_album(self, album_id: str) -> Album:
        try:
            # Try to parse as database ID first (for internal operations)
            if album_id.isdigit():
                django_album = await sync_to_async(self.model.objects.get)(
                    id=int(album_id)
                )
            else:
                # Fall back to spotify_gid for external API calls
                django_album = await sync_to_async(self.model.objects.get)(
                    spotify_gid=album_id
                )

            django_album.wanted = True
            await sync_to_async(django_album.save)()

            await sync_to_async(download_missing_albums_for_artist)(
                django_album.artist.id
            )
            return self._to_graphql_type(django_album)
        except ValueError:
            raise ValueError(f"Invalid album ID format: {album_id}")
        except self.model.DoesNotExist:
            raise ValueError(f"Album with ID {album_id} not found")
        except Exception as e:
            raise Exception(f"Error downloading album: {str(e)}")

    async def set_album_wanted(self, album_id: int, wanted: bool) -> MutationResult:
        try:
            # Perform DB work in a thread to avoid blocking
            django_album = await sync_to_async(
                lambda: self.model.objects.select_related("artist").get(id=album_id)
            )()
        except self.model.DoesNotExist:
            return MutationResult(success=False, message="Album not found", album=None)
        except Exception as e:
            return MutationResult(
                success=False, message=f"Error updating album: {e}", album=None
            )

        try:
            django_album.wanted = wanted
            await sync_to_async(django_album.save)()
        except Exception as e:
            return MutationResult(
                success=False, message=f"Error updating album: {e}", album=None
            )

        return MutationResult(
            success=True,
            message="Album wanted status updated successfully",
            album=self._to_graphql_type(django_album),
        )

    def _to_graphql_type(self, django_album: DjangoAlbum) -> Album:
        raw_id = getattr(django_album, "id", None)
        safe_id: int = int(raw_id) if isinstance(raw_id, (int, str)) else 0
        return Album(
            id=safe_id,
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
