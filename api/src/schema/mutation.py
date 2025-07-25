from typing import Optional
import strawberry
from ..types.models import (
    Artist, Album, Playlist,
    TrackArtistInput, TrackPlaylistInput,
    UpdateArtistInput, UpdateAlbumInput, UpdatePlaylistInput
)
from ..services import services

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def track_artist(self, input: TrackArtistInput) -> Artist:
        return await services.artist.track_artist(
            artist_id=input.artist_id,
            auto_download=input.auto_download
        )

    @strawberry.mutation
    async def update_artist(self, input: UpdateArtistInput) -> Artist:
        return await services.artist.update_artist(
            artist_id=input.artist_id,
            is_tracked=input.is_tracked,
            auto_download=input.auto_download
        )

    @strawberry.mutation
    async def update_album(self, input: UpdateAlbumInput) -> Album:
        return await services.album.update_album(
            album_id=input.album_id,
            is_wanted=input.is_wanted
        )

    @strawberry.mutation
    async def track_playlist(self, input: TrackPlaylistInput) -> Playlist:
        return await services.playlist.track_playlist(
            playlist_id=input.playlist_id,
            auto_track_artists=input.auto_track_artists
        )

    @strawberry.mutation
    async def update_playlist(self, input: UpdatePlaylistInput) -> Playlist:
        return await services.playlist.update_playlist(
            playlist_id=input.playlist_id,
            is_tracked=input.is_tracked,
            auto_track_artists=input.auto_track_artists
        )

    @strawberry.mutation
    async def sync_artist(self, artist_id: str) -> Artist:
        return await services.artist.sync_artist(artist_id)

    @strawberry.mutation
    async def sync_playlist(self, playlist_id: str) -> Playlist:
        return await services.playlist.sync_playlist(playlist_id)

    @strawberry.mutation
    async def download_album(self, album_id: str) -> Album:
        return await services.album.download_album(album_id) 