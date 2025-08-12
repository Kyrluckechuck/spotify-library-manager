import strawberry

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


@strawberry.type
class Mutation:
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
        self, playlist_id: int, name: str, auto_track_artists: bool
    ) -> "MutationResult":
        return await services.playlist.update_playlist(
            playlist_id=playlist_id,
            name=name,
            auto_track_artists=auto_track_artists,
        )

    @strawberry.mutation
    async def sync_artist(self, artist_id: str) -> Artist:
        return await services.artist.sync_artist(artist_id)

    @strawberry.mutation
    async def sync_playlist(self, playlist_id: int) -> "MutationResult":
        return await services.playlist.sync_playlist(playlist_id)

    @strawberry.mutation
    async def download_album(self, album_id: str) -> Album:
        return await services.album.download_album(album_id)

    @strawberry.mutation
    async def download_url(
        self, url: str, auto_track_artists: bool = False
    ) -> "MutationResult":
        return await services.downloader.download_url(
            url=url, auto_track_artists=auto_track_artists
        )

    @strawberry.mutation
    async def create_playlist(
        self, name: str, url: str, auto_track_artists: bool = False
    ) -> Playlist:
        return await services.playlist.create_playlist(
            name=name, url=url, auto_track_artists=auto_track_artists
        )

    @strawberry.mutation
    async def cancel_all_pending_tasks(self) -> "MutationResult":
        """Cancel all pending tasks in the Huey queue."""
        return services.task_management.cancel_all_pending_tasks()

    @strawberry.mutation
    async def cancel_tasks_by_name(self, task_name: str) -> "MutationResult":
        """Cancel all pending tasks with a specific name."""
        return services.task_management.cancel_tasks_by_name(task_name=task_name)

    @strawberry.mutation
    async def cancel_running_tasks_by_name(self, task_name: str) -> "MutationResult":
        """Cancel running tasks with a specific name."""
        return services.task_management.cancel_running_tasks_by_name(
            task_name=task_name
        )

    @strawberry.mutation
    async def cancel_all_tasks(self) -> "MutationResult":
        """Cancel both pending and running tasks."""
        return services.task_management.cancel_all_tasks()
