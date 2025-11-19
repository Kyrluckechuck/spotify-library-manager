import re
from typing import List, Optional
from urllib.parse import urlparse

import strawberry
from asgiref.sync import sync_to_async

from ..graphql_types.models import (
    Album,
    Artist,
    MutationResult,
    Playlist,
    TrackPlaylistInput,
    UpdateAlbumInput,
    UpdateArtistInput,
)
from ..services import services


def validate_url(url: str) -> MutationResult:
    """Validate URL format and scheme."""
    if not url or not url.strip():
        return MutationResult(success=False, message="URL cannot be empty")

    try:
        parsed = urlparse(url.strip())
        if not parsed.scheme or not parsed.netloc:
            return MutationResult(success=False, message="Invalid URL format")
        if parsed.scheme not in ("http", "https"):
            return MutationResult(
                success=False, message="URL must use http or https scheme"
            )
        return MutationResult(success=True, message="URL valid")
    except Exception:
        return MutationResult(success=False, message="Invalid URL format")


def validate_name(name: str, field_name: str = "Name") -> MutationResult:
    """Validate name length and content."""
    if not name or not name.strip():
        return MutationResult(success=False, message=f"{field_name} cannot be empty")

    name = name.strip()
    if len(name) > 255:
        return MutationResult(
            success=False, message=f"{field_name} cannot exceed 255 characters"
        )
    if len(name) < 1:
        return MutationResult(
            success=False, message=f"{field_name} must be at least 1 character"
        )

    return MutationResult(success=True, message=f"{field_name} valid")


def validate_task_name(task_name: str) -> MutationResult:
    """Validate task name format."""
    if not task_name or not task_name.strip():
        return MutationResult(success=False, message="Task name cannot be empty")

    task_name = task_name.strip()
    # Allow alphanumeric, dots, underscores, and hyphens
    if not re.match(r"^[a-zA-Z0-9._-]+$", task_name):
        return MutationResult(
            success=False,
            message="Task name can only contain letters, numbers, dots, underscores, and hyphens",
        )

    return MutationResult(success=True, message="Task name valid")


@strawberry.type
class Mutation:  # pylint: disable=too-many-public-methods
    @strawberry.mutation
    async def track_artist(self, artist_id: int) -> "MutationResult":
        return await services.artist.track_artist(artist_id=artist_id)

    @strawberry.mutation
    async def untrack_artist(self, artist_id: int) -> "MutationResult":
        return await services.artist.untrack_artist(artist_id=artist_id)

    @strawberry.mutation
    async def update_artist(self, input: UpdateArtistInput) -> Artist:
        return await services.artist.update_artist(
            artist_id=input.artist_id,
            is_tracked=input.is_tracked,
            auto_download=input.auto_download,
        )

    @strawberry.mutation
    async def set_album_wanted(self, album_id: int, wanted: bool) -> "MutationResult":
        return await services.album.set_album_wanted(album_id=album_id, wanted=wanted)

    @strawberry.mutation
    async def update_album(self, input: UpdateAlbumInput) -> Album:
        return await services.album.update_album(
            album_id=input.album_id, is_wanted=input.is_wanted
        )

    @strawberry.mutation
    async def toggle_playlist(self, playlist_id: int) -> "MutationResult":
        return await services.playlist.toggle_playlist(playlist_id=playlist_id)

    @strawberry.mutation
    async def toggle_playlist_auto_track(self, playlist_id: int) -> "MutationResult":
        return await services.playlist.toggle_playlist_auto_track(
            playlist_id=playlist_id
        )

    @strawberry.mutation
    async def track_playlist(self, input: TrackPlaylistInput) -> Playlist:
        return await services.playlist.track_playlist(
            playlist_id=input.playlist_id, auto_track_artists=input.auto_track_artists
        )

    @strawberry.mutation
    async def update_playlist(
        self, playlist_id: int, name: str, url: str, auto_track_artists: bool
    ) -> "MutationResult":
        name_validation = validate_name(name, "Playlist name")
        if not name_validation.success:
            return name_validation

        url_validation = validate_url(url)
        if not url_validation.success:
            return url_validation

        return await services.playlist.update_playlist(
            playlist_id=playlist_id,
            name=name.strip(),
            url=url.strip(),
            auto_track_artists=auto_track_artists,
        )

    @strawberry.mutation
    async def sync_artist(self, artist_id: str) -> Artist:
        return await services.artist.sync_artist(artist_id)

    @strawberry.mutation
    async def download_artist(self, artist_id: str) -> "MutationResult":
        return await services.artist.download_artist(artist_id)

    @strawberry.mutation
    async def sync_playlist(
        self, playlist_id: int, force: bool = False
    ) -> "MutationResult":
        return await services.playlist.sync_playlist(playlist_id, force=force)

    @strawberry.mutation
    async def download_album(self, album_id: str) -> Album:
        return await services.album.download_album(album_id)

    @strawberry.mutation
    async def download_url(
        self, url: str, auto_track_artists: bool = False
    ) -> "MutationResult":
        validation_result = validate_url(url)
        if not validation_result.success:
            return validation_result

        return await services.downloader.download_url(
            url=url.strip(), auto_track_artists=auto_track_artists
        )

    @strawberry.mutation
    async def create_playlist(
        self, name: str, url: str, auto_track_artists: bool = False
    ) -> Playlist:
        name_validation = validate_name(name, "Playlist name")
        if not name_validation.success:
            # Return a failure result as a Playlist-like response (this will need error handling)
            raise ValueError(name_validation.message)

        url_validation = validate_url(url)
        if not url_validation.success:
            raise ValueError(url_validation.message)

        return await services.playlist.create_playlist(
            name=name.strip(), url=url.strip(), auto_track_artists=auto_track_artists
        )

    @strawberry.mutation
    async def cancel_all_pending_tasks(self) -> "MutationResult":
        """Cancel all pending tasks in the Huey queue."""
        return await services.task_management.cancel_all_pending_tasks()

    @strawberry.mutation
    async def cancel_tasks_by_name(self, task_name: str) -> "MutationResult":
        """Cancel all pending tasks with a specific name."""
        validation_result = validate_task_name(task_name)
        if not validation_result.success:
            return validation_result

        return await services.task_management.cancel_tasks_by_name(
            task_name=task_name.strip()
        )

    @strawberry.mutation
    async def cancel_running_tasks_by_name(self, task_name: str) -> "MutationResult":
        """Cancel running tasks with a specific name."""
        validation_result = validate_task_name(task_name)
        if not validation_result.success:
            return validation_result

        return await services.task_management.cancel_running_tasks_by_name(
            task_name=task_name.strip()
        )

    @strawberry.mutation
    async def cancel_all_tasks(self) -> "MutationResult":
        """Cancel both pending and running tasks."""
        return await services.task_management.cancel_all_tasks()

    @strawberry.mutation
    async def sync_all_tracked_artists(self) -> "MutationResult":
        """Sync all tracked artists in batch."""
        try:
            from library_manager.helpers import enqueue_artist_sync_with_download
            from library_manager.models import Artist

            tracked_artists: list = await sync_to_async(list)(
                Artist.objects.filter(tracked=True)
            )

            if not tracked_artists:
                return MutationResult(
                    success=True, message="No tracked artists found to sync"
                )

            # Use database IDs for batch operations with sync_to_async
            operation_counts = await sync_to_async(enqueue_artist_sync_with_download)(
                Artist.objects.filter(tracked=True),
                auto_download=True,
                delay_seconds=5,  # Rate limiting
            )

            total_operations = sum(operation_counts.values())
            return MutationResult(
                success=True,
                message=f"Enqueued {total_operations} operations for {len(tracked_artists)} tracked artists",
            )
        except Exception as e:
            return MutationResult(
                success=False, message=f"Failed to sync tracked artists: {str(e)}"
            )

    @strawberry.mutation
    async def batch_artist_operations(
        self, artist_ids: List[int], operations: Optional[List[str]] = None
    ) -> "MutationResult":
        """Perform batch operations on multiple artists using database IDs."""
        try:
            from library_manager.helpers import enqueue_batch_artist_operations
            from library_manager.models import Artist

            if not artist_ids:
                return MutationResult(success=False, message="No artist IDs provided")

            # Get artists by database IDs
            artists: list = await sync_to_async(list)(
                Artist.objects.filter(id__in=artist_ids)
            )

            if not artists:
                return MutationResult(
                    success=False, message="No artists found with provided IDs"
                )

            # Default operations if none specified
            if operations is None:
                operations = ["fetch", "download"]

            # Use database IDs for batch operations with sync_to_async
            operation_counts = await sync_to_async(enqueue_batch_artist_operations)(
                Artist.objects.filter(id__in=artist_ids), operations=operations
            )

            total_operations = sum(operation_counts.values())
            return MutationResult(
                success=True,
                message=f"Enqueued {total_operations} operations for {len(artists)} artists",
            )
        except Exception as e:
            return MutationResult(
                success=False, message=f"Failed to enqueue batch operations: {str(e)}"
            )

    @strawberry.mutation
    async def disconnect_spotify(self) -> MutationResult:
        """Disconnect Spotify OAuth account by removing stored tokens."""
        try:
            from library_manager.models import SpotifyOAuthToken

            await sync_to_async(SpotifyOAuthToken.objects.filter(id=1).delete)()
            return MutationResult(
                success=True, message="Spotify account disconnected successfully"
            )
        except Exception as e:
            return MutationResult(
                success=False, message=f"Failed to disconnect: {str(e)}"
            )
