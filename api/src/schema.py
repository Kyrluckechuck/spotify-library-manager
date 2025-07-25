from typing import List, Optional
import strawberry
from asgiref.sync import sync_to_async
from library_manager.models import Artist as DjangoArtist
from library_manager.models import Album as DjangoAlbum
from library_manager.models import Song as DjangoSong
from library_manager.models import TrackedPlaylist as DjangoTrackedPlaylist

@strawberry.type
class Artist:
    id: int
    name: str
    gid: str
    tracked: bool
    added_at: Optional[str] = None
    last_synced_at: Optional[str] = None
    
    @classmethod
    def from_django(cls, django_artist: DjangoArtist) -> "Artist":
        return cls(
            id=django_artist.id,
            name=django_artist.name,
            gid=django_artist.gid,
            tracked=django_artist.tracked,
            added_at=django_artist.added_at.isoformat() if django_artist.added_at else None,
            last_synced_at=django_artist.last_synced_at.isoformat() if django_artist.last_synced_at else None,
        )

@strawberry.type
class Album:
    id: int
    spotify_gid: str
    spotify_uri: str
    name: str
    total_tracks: int
    downloaded: bool
    wanted: bool
    album_type: Optional[str] = None
    album_group: Optional[str] = None
    
    @classmethod
    def from_django(cls, django_album: DjangoAlbum) -> "Album":
        return cls(
            id=django_album.id,
            spotify_gid=django_album.spotify_gid or "",
            spotify_uri=django_album.spotify_uri or "",
            name=django_album.name,
            total_tracks=django_album.total_tracks or 0,
            downloaded=django_album.downloaded,
            wanted=django_album.wanted,
            album_type=django_album.album_type,
            album_group=django_album.album_group,
        )

@strawberry.type
class Song:
    id: int
    name: str
    gid: str
    created_at: str
    failed_count: int
    bitrate: Optional[int] = None
    unavailable: bool
    file_path: Optional[str] = None
    downloaded: bool
    spotify_uri: str
    
    @classmethod
    def from_django(cls, django_song: DjangoSong) -> "Song":
        return cls(
            id=django_song.id,
            name=django_song.name,
            gid=django_song.gid,
            created_at=django_song.created_at.isoformat(),
            failed_count=django_song.failed_count,
            bitrate=django_song.bitrate,
            unavailable=django_song.unavailable,
            file_path=django_song.file_path,
            downloaded=django_song.downloaded,
            spotify_uri=django_song.spotify_uri,
        )

@strawberry.type
class TrackedPlaylist:
    id: int
    name: str
    url: str
    enabled: bool
    auto_track_artists: bool
    last_synced_at: Optional[str] = None
    
    @classmethod
    def from_django(cls, django_playlist: DjangoTrackedPlaylist) -> "TrackedPlaylist":
        return cls(
            id=django_playlist.id,
            name=django_playlist.name,
            url=django_playlist.url,
            enabled=django_playlist.enabled,
            auto_track_artists=django_playlist.auto_track_artists,
            last_synced_at=django_playlist.last_synced_at.isoformat() if django_playlist.last_synced_at else None,
        )

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello from Spotify Library Manager API!"
    
    @strawberry.field
    async def artists(self, tracked: Optional[bool] = None, limit: int = 20) -> List[Artist]:
        @sync_to_async
        def get_artists():
            qs = DjangoArtist.objects.all()
            if tracked is not None:
                qs = qs.filter(tracked=tracked)
            return list(qs[:limit])
        
        django_artists = await get_artists()
        return [Artist.from_django(artist) for artist in django_artists]

    @strawberry.field
    async def albums(self, artist_id: Optional[int] = None, limit: int = 20) -> List[Album]:
        @sync_to_async
        def get_albums():
            qs = DjangoAlbum.objects.all()
            if artist_id:
                qs = qs.filter(artist_id=artist_id)
            return list(qs[:limit])
        
        django_albums = await get_albums()
        return [Album.from_django(album) for album in django_albums]

    @strawberry.field
    async def songs(self, artist_id: Optional[int] = None, limit: int = 20) -> List[Song]:
        @sync_to_async
        def get_songs():
            qs = DjangoSong.objects.all()
            if artist_id:
                qs = qs.filter(primary_artist_id=artist_id)
            return list(qs[:limit])
        
        django_songs = await get_songs()
        return [Song.from_django(song) for song in django_songs]

    @strawberry.field
    async def playlists(self, enabled: Optional[bool] = None, limit: int = 20) -> List[TrackedPlaylist]:
        @sync_to_async
        def get_playlists():
            qs = DjangoTrackedPlaylist.objects.all()
            if enabled is not None:
                qs = qs.filter(enabled=enabled)
            return list(qs[:limit])
        
        django_playlists = await get_playlists()
        return [TrackedPlaylist.from_django(playlist) for playlist in django_playlists]

schema = strawberry.Schema(query=Query) 