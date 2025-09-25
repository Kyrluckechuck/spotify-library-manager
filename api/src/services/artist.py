# mypy: disable-error-code=attr-defined
from typing import Any, List, Optional, Tuple

from django.conf import settings
from django.db.models import Q

from asgiref.sync import sync_to_async
from downloader import utils

from library_manager.models import Album
from library_manager.models import Artist as DjangoArtist
from library_manager.tasks import (
    download_missing_albums_for_artist,
    fetch_all_albums_for_artist_sync,
)

from ..graphql_types.models import Artist, MutationResult
from .base import BaseService


class ArtistService(BaseService[Artist]):
    def __init__(self) -> None:
        super().__init__()
        self.model = DjangoArtist

    async def get_by_id(self, id: str) -> Optional[Artist]:
        try:
            # First try to find by GID
            django_artist = await self.model.objects.aget(gid=id)
            return await self._to_graphql_type_async(django_artist)
        except self.model.DoesNotExist:
            try:
                # If not found by GID, try to find by database ID
                django_artist = await self.model.objects.aget(id=int(id))
                return await self._to_graphql_type_async(django_artist)
            except (self.model.DoesNotExist, ValueError):
                return None

    async def get_connection(
        self,
        first: int = 20,
        after: Optional[str] = None,
        **filters: Any,
    ) -> Tuple[List[Artist], bool, int]:
        is_tracked: Optional[bool] = filters.get("is_tracked")
        search: Optional[str] = filters.get("search")
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
        total_count = await sync_to_async(queryset.count)()

        # Get one extra item to determine if there are more pages
        def fetch_items() -> List[DjangoArtist]:
            return list(queryset.order_by("id")[: first + 1])

        items: List[DjangoArtist] = await sync_to_async(fetch_items)()

        has_next_page = len(items) > first
        items = items[:first]  # Remove the extra item

        # Convert items to GraphQL types with async undownloaded counts
        graphql_items = []
        for item in items:
            graphql_item = await self._to_graphql_type_async(item)
            graphql_items.append(graphql_item)

        return (
            graphql_items,
            has_next_page,
            total_count,
        )

    async def track_artist(self, artist_id: int) -> MutationResult:
        try:
            django_artist = await sync_to_async(self.model.objects.get)(id=artist_id)
            django_artist.tracked = True
            await sync_to_async(django_artist.save)()

            # Queue tasks
            # await sync_to_async(fetch_all_albums_for_artist)(django_artist.id)

            return MutationResult(
                success=True,
                message="Artist tracked successfully",
                artist=await self._to_graphql_type_async(django_artist),
            )
        except self.model.DoesNotExist:
            return MutationResult(
                success=False, message="Artist not found", artist=None
            )
        except Exception as e:
            return MutationResult(
                success=False, message=f"Error tracking artist: {str(e)}", artist=None
            )

    async def untrack_artist(self, artist_id: int) -> MutationResult:
        try:
            django_artist = await sync_to_async(self.model.objects.get)(id=artist_id)
            django_artist.tracked = False
            await sync_to_async(django_artist.save)()

            return MutationResult(
                success=True,
                message="Artist untracked successfully",
                artist=await self._to_graphql_type_async(django_artist),
            )
        except self.model.DoesNotExist:
            return MutationResult(
                success=False, message="Artist not found", artist=None
            )
        except Exception as e:
            return MutationResult(
                success=False, message=f"Error untracking artist: {str(e)}", artist=None
            )

    async def update_artist(
        self,
        artist_id: str,
        is_tracked: Optional[bool] = None,
        auto_download: Optional[bool] = None,
    ) -> Artist:
        django_artist = await self.model.objects.aget(gid=artist_id)

        if is_tracked is not None:
            django_artist.tracked = is_tracked

        if auto_download and not django_artist.tracked:
            django_artist.tracked = True

        await django_artist.asave()

        if auto_download:
            await sync_to_async(download_missing_albums_for_artist)(django_artist.id)

        return await self._to_graphql_type_async(django_artist)

    async def sync_artist(self, artist_id: str) -> Artist:
        try:
            # Convert string to int since frontend sends database ID
            artist_db_id = int(artist_id)
            django_artist = await sync_to_async(self.model.objects.get)(id=artist_db_id)
            await sync_to_async(fetch_all_albums_for_artist_sync)(django_artist.id)
            return await self._to_graphql_type_async(django_artist)
        except ValueError as exc:
            raise ValueError(f"Invalid artist ID format: {artist_id}") from exc
        except self.model.DoesNotExist as exc:
            raise ValueError(f"Artist with ID {artist_id} not found") from exc
        except Exception as e:
            raise RuntimeError(f"Error syncing artist: {str(e)}") from e

    async def download_artist(self, artist_id: str) -> MutationResult:
        try:
            # Convert string to int since frontend sends database ID
            artist_db_id = int(artist_id)
            django_artist = await sync_to_async(self.model.objects.get)(id=artist_db_id)

            # Start download task for missing albums
            await sync_to_async(download_missing_albums_for_artist.delay)(
                django_artist.id
            )

            return MutationResult(
                success=True, message=f"Download started for {django_artist.name}"
            )
        except ValueError:
            return MutationResult(
                success=False, message=f"Invalid artist ID format: {artist_id}"
            )
        except self.model.DoesNotExist:
            return MutationResult(
                success=False, message=f"Artist with ID {artist_id} not found"
            )
        except Exception as e:
            return MutationResult(
                success=False, message=f"Error starting download for artist: {str(e)}"
            )

    async def _get_undownloaded_count(self, django_artist: DjangoArtist) -> int:
        """Calculate undownloaded count for an artist asynchronously."""
        album_types_to_download = getattr(
            settings, "ALBUM_TYPES_TO_DOWNLOAD", ["single", "album", "compilation"]
        )
        album_groups_to_ignore = getattr(
            settings, "ALBUM_GROUPS_TO_IGNORE", ["appears_on"]
        )

        return await sync_to_async(
            lambda: Album.objects.filter(
                artist=django_artist,
                downloaded=False,
                wanted=True,
                album_type__in=album_types_to_download,
            )
            .exclude(album_group__in=album_groups_to_ignore)
            .count()
        )()

    async def _to_graphql_type_async(self, django_artist: DjangoArtist) -> Artist:
        """Convert Django artist to GraphQL type with async database operations."""
        # Some unit tests use light mocks without an `id`; be defensive here
        raw_id = getattr(django_artist, "id", None)
        safe_id: int = int(raw_id) if isinstance(raw_id, (int, str)) else 0

        # Convert GID to Spotify URI for proper URL generation
        spotify_uri = utils.gid_to_uri(django_artist.gid)

        # Calculate undownloaded count asynchronously
        undownloaded_count = await self._get_undownloaded_count(django_artist)

        return Artist(
            id=safe_id,
            name=django_artist.name,
            gid=django_artist.gid,
            spotify_uri=spotify_uri,
            is_tracked=django_artist.tracked,
            last_synced=(
                django_artist.last_synced_at.isoformat()
                if django_artist.last_synced_at
                else None
            ),
            added_at=(
                django_artist.added_at.isoformat()
                if hasattr(django_artist, "added_at") and django_artist.added_at
                else None
            ),
            undownloaded_count=undownloaded_count,
        )

    def _to_graphql_type(self, django_artist: DjangoArtist) -> Artist:
        """Convert Django artist to GraphQL type (sync version without count)."""
        # Some unit tests use light mocks without an `id`; be defensive here
        raw_id = getattr(django_artist, "id", None)
        safe_id: int = int(raw_id) if isinstance(raw_id, (int, str)) else 0

        # Convert GID to Spotify URI for proper URL generation
        spotify_uri = utils.gid_to_uri(django_artist.gid)

        return Artist(
            id=safe_id,
            name=django_artist.name,
            gid=django_artist.gid,
            spotify_uri=spotify_uri,
            is_tracked=django_artist.tracked,
            last_synced=(
                django_artist.last_synced_at.isoformat()
                if django_artist.last_synced_at
                else None
            ),
            added_at=(
                django_artist.added_at.isoformat()
                if hasattr(django_artist, "added_at") and django_artist.added_at
                else None
            ),
            undownloaded_count=0,  # Default to 0 for sync contexts
        )
