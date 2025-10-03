# mypy: disable-error-code=attr-defined
import re
from typing import Any, List, Optional, Tuple, cast

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

    def _normalize_spotify_url(self, url: str) -> str:
        """Convert various Spotify URL formats to a standard format, stripping tracking parameters."""
        # Handle spotify: URIs (already normalized)
        if url.startswith("spotify:"):
            return url

        # Handle web URLs - extract content type and ID, ignoring parameters
        if "open.spotify.com" in url:
            match = re.search(r"open\.spotify\.com/([^/?]+)/([^/?]+)", url)
            if match:
                content_type, content_id = match.groups()
                return f"spotify:{content_type}:{content_id}"

        return url

    def _find_duplicate_playlist(self, normalized_url: str) -> Optional[DjangoPlaylist]:
        """Find existing playlist that matches the normalized URL in either format."""
        # First check for exact match with normalized URL
        existing = cast(
            Optional[DjangoPlaylist],
            self.model.objects.filter(url=normalized_url).first(),
        )
        if existing:
            return existing

        # If normalized_url is a URI, also check for HTTP format
        if normalized_url.startswith("spotify:"):
            # Convert URI back to HTTP format to check existing HTTP URLs
            parts = normalized_url.split(":")
            if len(parts) == 3:
                content_type, content_id = parts[1], parts[2]
                http_url = f"https://open.spotify.com/{content_type}/{content_id}"

                # Check for HTTP URLs with various parameter patterns
                existing = cast(
                    Optional[DjangoPlaylist],
                    self.model.objects.filter(
                        Q(url=http_url)
                        | Q(
                            url__startswith=f"{http_url}?"
                        )  # Match URLs with parameters
                    ).first(),
                )
                if existing:
                    return existing

        return None

    def _find_duplicate_playlist_excluding(
        self, normalized_url: str, exclude_id: int
    ) -> Optional[DjangoPlaylist]:
        """Find existing playlist that matches the normalized URL, excluding the specified ID."""
        # First check for exact match with normalized URL
        existing = cast(
            Optional[DjangoPlaylist],
            (
                self.model.objects.filter(url=normalized_url)
                .exclude(id=exclude_id)
                .first()
            ),
        )
        if existing:
            return existing

        # If normalized_url is a URI, also check for HTTP format
        if normalized_url.startswith("spotify:"):
            # Convert URI back to HTTP format to check existing HTTP URLs
            parts = normalized_url.split(":")
            if len(parts) == 3:
                content_type, content_id = parts[1], parts[2]
                http_url = f"https://open.spotify.com/{content_type}/{content_id}"

                # Check for HTTP URLs with various parameter patterns
                existing = cast(
                    Optional[DjangoPlaylist],
                    (
                        self.model.objects.filter(
                            Q(url=http_url)
                            | Q(
                                url__startswith=f"{http_url}?"
                            )  # Match URLs with parameters
                        )
                        .exclude(id=exclude_id)
                        .first()
                    ),
                )
                if existing:
                    return existing

        return None

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
        sort_by = (
            filters.get("sort_by") if isinstance(filters.get("sort_by"), str) else None
        )
        sort_direction = (
            filters.get("sort_direction")
            if isinstance(filters.get("sort_direction"), str)
            else None
        )
        queryset = self.model.objects.all()

        # Apply filters
        if enabled is not None:
            queryset = queryset.filter(enabled=enabled)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(url__icontains=search)
            )

        # Apply sorting
        sort_field_map: dict[str, str] = {
            "name": "name",
            "enabled": "enabled",
            "autoTrackArtists": "auto_track_artists",
            "lastSyncedAt": "last_synced_at",
        }

        order_field = "id"  # default
        if isinstance(sort_by, str):
            mapped_field = sort_field_map.get(sort_by)
            if mapped_field is not None:
                order_field = mapped_field
                if sort_direction == "desc":
                    order_field = f"-{order_field}"

        # Apply cursor-based pagination
        if after:
            id_after = self.decode_cursor(after)
            queryset = queryset.filter(id__gt=id_after)

        # Get total count before slicing
        total_count = await sync_to_async(queryset.count)()

        # Get one extra item to determine if there are more pages
        def fetch_items() -> List[DjangoPlaylist]:
            return list(queryset.order_by(order_field, "id")[: first + 1])

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
        """Create a new playlist, checking for duplicates using normalized URLs."""
        # Normalize the URL to strip tracking parameters for deduplication
        normalized_url = self._normalize_spotify_url(url)

        # Check for duplicates against both normalized URI and potential HTTP format
        existing_playlist = await sync_to_async(
            lambda: self._find_duplicate_playlist(normalized_url)
        )()

        if existing_playlist:
            # Return the existing playlist instead of creating a duplicate
            return self._to_graphql_type(existing_playlist)

        django_playlist = self.model(
            name=name,
            url=normalized_url,  # Store the normalized URL
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

            # Normalize the URL to strip tracking parameters
            normalized_url = self._normalize_spotify_url(url)

            # Check if another playlist already has this normalized URL
            # Only check if the URL is actually changing
            current_normalized = self._normalize_spotify_url(django_playlist.url)
            if normalized_url != current_normalized:
                existing_playlist = await sync_to_async(
                    lambda: self._find_duplicate_playlist_excluding(
                        normalized_url, playlist_id
                    )
                )()

                if existing_playlist:
                    return MutationResult(
                        success=False,
                        message=f"A playlist with this URL already exists: {existing_playlist.name}",
                    )

            django_playlist.name = name
            django_playlist.url = normalized_url
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

    async def sync_playlist(
        self, playlist_id: int, force: bool = False
    ) -> MutationResult:
        try:
            django_playlist = await sync_to_async(self.model.objects.get)(
                id=playlist_id
            )

            if force:
                # For force sync, directly queue the download_playlist task with force_playlist_resync=True
                from library_manager.tasks import download_playlist

                await sync_to_async(download_playlist.delay)(
                    playlist_url=django_playlist.url,
                    tracked=django_playlist.auto_track_artists,
                    force_playlist_resync=True,
                )
                message = "Playlist force sync started successfully"
            else:
                # Trigger normal sync task (queue it for Celery worker)
                await sync_to_async(sync_tracked_playlist.delay)(django_playlist.id)
                message = "Playlist sync started successfully"

            return MutationResult(
                success=True,
                message=message,
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
