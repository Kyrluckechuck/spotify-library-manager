# mypy: disable-error-code=attr-defined
from typing import Any, List, Optional, Tuple

from django.db.models import Q

from asgiref.sync import sync_to_async

from library_manager.models import TrackedPlaylist as DjangoPlaylist
from library_manager.tasks import sync_tracked_playlist, sync_tracked_playlist_artists

from ..graphql_types.models import MutationResult, Playlist
from .base import BaseService


class PlaylistService(BaseService[Playlist]):
    def __init__(self) -> None:
        super().__init__()
        self.model = DjangoPlaylist

    async def get_by_id(self, id: str) -> Optional[Playlist]:
        try:
            # First try to find by database ID (more specific)
            django_playlist = await sync_to_async(self.model.objects.get)(id=int(id))
            return self._to_graphql_type(django_playlist)
        except (self.model.DoesNotExist, ValueError):
            try:
                # If not found by database ID, try to find by URL containing the ID
                django_playlist = await sync_to_async(self.model.objects.get)(
                    url__contains=id
                )
                return self._to_graphql_type(django_playlist)
            except (self.model.DoesNotExist, self.model.MultipleObjectsReturned):
                return None

    async def get_connection(
        self,
        first: int = 20,
        after: Optional[str] = None,
        **filters: Any,
    ) -> Tuple[List[Playlist], bool, int]:
        enabled: Optional[bool] = filters.get("enabled")
        search: Optional[str] = filters.get("search")
        queryset = self.model.objects.all()

        # Apply filters
        if enabled is not None:
            queryset = queryset.filter(enabled=enabled)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(url__icontains=search)
            )

        # Apply cursor-based pagination
        if after:
            id_after = self.decode_cursor(after)
            queryset = queryset.filter(id__gt=id_after)

        # Get total count before slicing
        total_count = await sync_to_async(queryset.count)()

        # Get one extra item to determine if there are more pages
        def fetch_items() -> List[DjangoPlaylist]:
            return list(queryset.order_by("id")[: first + 1])

        items: List[DjangoPlaylist] = await sync_to_async(fetch_items)()

        has_next_page = len(items) > first
        items = items[:first]  # Remove the extra item

        return (
            [self._to_graphql_type(item) for item in items],
            has_next_page,
            total_count,
        )

    async def track_playlist(
        self, playlist_id: str, auto_track_artists: bool = False
    ) -> Playlist:
        django_playlist = await sync_to_async(self.model.objects.get)(
            url__contains=playlist_id
        )
        django_playlist.enabled = True
        django_playlist.auto_track_artists = auto_track_artists
        await sync_to_async(django_playlist.save)()

        # Queue tasks
        sync_tracked_playlist.delay(django_playlist.id)
        if auto_track_artists:
            sync_tracked_playlist_artists.delay(django_playlist.id)

        return self._to_graphql_type(django_playlist)

    async def create_playlist(
        self, name: str, url: str, auto_track_artists: bool = False
    ) -> Playlist:
        """Create a new playlist."""
        django_playlist = self.model(
            name=name,
            url=url,
            enabled=True,
            auto_track_artists=auto_track_artists,
        )
        await sync_to_async(django_playlist.save)()

        # Queue tasks
        sync_tracked_playlist.delay(django_playlist.id)
        if auto_track_artists:
            sync_tracked_playlist_artists.delay(django_playlist.id)

        return self._to_graphql_type(django_playlist)

    async def update_playlist(
        self,
        playlist_id: int,
        name: str,
        url: str,
        auto_track_artists: bool,
    ) -> MutationResult:
        try:
            django_playlist = await sync_to_async(self.model.objects.get)(
                id=playlist_id
            )

            django_playlist.name = name
            django_playlist.url = url
            django_playlist.auto_track_artists = auto_track_artists

            await sync_to_async(django_playlist.save)()

            return MutationResult(
                success=True,
                message="Playlist updated successfully",
                playlist=self._to_graphql_type(django_playlist),
            )
        except self.model.DoesNotExist:
            return MutationResult(
                success=False, message="Playlist not found", playlist=None
            )
        except Exception as e:
            return MutationResult(
                success=False,
                message=f"Error updating playlist: {str(e)}",
                playlist=None,
            )

    async def sync_playlist(self, playlist_id: int) -> MutationResult:
        try:
            django_playlist = await sync_to_async(self.model.objects.get)(
                id=playlist_id
            )

            # Trigger sync task (queue it for Celery worker)
            await sync_to_async(sync_tracked_playlist.delay)(django_playlist.id)

            return MutationResult(
                success=True,
                message="Playlist sync started successfully",
                playlist=self._to_graphql_type(django_playlist),
            )
        except self.model.DoesNotExist:
            return MutationResult(
                success=False, message="Playlist not found", playlist=None
            )
        except Exception as e:
            return MutationResult(
                success=False,
                message=f"Error syncing playlist: {str(e)}",
                playlist=None,
            )

    async def toggle_playlist(self, playlist_id: int) -> MutationResult:
        try:
            django_playlist = await sync_to_async(self.model.objects.get)(
                id=playlist_id
            )
            django_playlist.enabled = not django_playlist.enabled
            await sync_to_async(django_playlist.save)()

            return MutationResult(
                success=True,
                message="Playlist toggled successfully",
                playlist=self._to_graphql_type(django_playlist),
            )
        except self.model.DoesNotExist:
            return MutationResult(
                success=False, message="Playlist not found", playlist=None
            )
        except Exception as e:
            return MutationResult(
                success=False,
                message=f"Error toggling playlist: {str(e)}",
                playlist=None,
            )

    async def toggle_playlist_auto_track(self, playlist_id: int) -> MutationResult:
        try:
            django_playlist = await sync_to_async(self.model.objects.get)(
                id=playlist_id
            )
            django_playlist.auto_track_artists = not django_playlist.auto_track_artists
            await sync_to_async(django_playlist.save)()

            return MutationResult(
                success=True,
                message="Playlist auto-track toggled successfully",
                playlist=self._to_graphql_type(django_playlist),
            )
        except self.model.DoesNotExist:
            return MutationResult(
                success=False, message="Playlist not found", playlist=None
            )
        except Exception as e:
            return MutationResult(
                success=False,
                message=f"Error toggling playlist auto-track: {str(e)}",
                playlist=None,
            )

    def _to_graphql_type(self, django_playlist: DjangoPlaylist) -> Playlist:
        return Playlist(
            id=int(django_playlist.id),
            name=django_playlist.name,
            url=django_playlist.url,
            enabled=django_playlist.enabled,
            auto_track_artists=django_playlist.auto_track_artists,
            last_synced_at=(
                django_playlist.last_synced_at.isoformat()
                if django_playlist.last_synced_at
                else None
            ),
        )
