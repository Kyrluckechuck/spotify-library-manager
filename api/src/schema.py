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
    artist: Optional[str] = None  # Artist name

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
            artist=None,  # Will be populated in the resolver
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
class PageInfo:
    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[str] = None
    end_cursor: Optional[str] = None

@strawberry.type
class ArtistsConnection:
    edges: List[Artist]
    page_info: PageInfo
    total_count: int

@strawberry.type
class AlbumsConnection:
    edges: List[Album]
    page_info: PageInfo
    total_count: int

@strawberry.type
class SongsConnection:
    edges: List[Song]
    page_info: PageInfo
    total_count: int

@strawberry.type
class PlaylistsConnection:
    edges: List[TrackedPlaylist]
    page_info: PageInfo
    total_count: int

@strawberry.type
class MutationResult:
    success: bool
    message: str
    artist: Optional[Artist] = None
    album: Optional[Album] = None
    playlist: Optional[TrackedPlaylist] = None

@strawberry.type
class TaskResult:
    success: bool
    message: str
    task_id: Optional[str] = None

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello from Spotify Library Manager API!"

    @strawberry.field
    async def artists(
        self, 
        tracked: Optional[bool] = None, 
        first: int = 20,
        after: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_direction: Optional[str] = None
    ) -> ArtistsConnection:
        @sync_to_async
        def get_artists_page():
            # Build base queryset
            qs = DjangoArtist.objects.all()
            if tracked is not None:
                qs = qs.filter(tracked=tracked)
            
            # Apply sorting
            sort_field = 'id'  # default
            if sort_by == 'name':
                sort_field = 'name'
            elif sort_by == 'tracked':
                sort_field = 'tracked'
            elif sort_by == 'added_at':
                sort_field = 'added_at'
            elif sort_by == 'last_synced_at':
                sort_field = 'last_synced_at'
            
            # Apply sort direction
            if sort_direction == 'desc':
                sort_field = f'-{sort_field}'
            
            qs = qs.order_by(sort_field, 'id')  # Always include id for consistent pagination
            
            # Get total count
            total_count = qs.count()
            
            # Handle cursor pagination - need to be smarter about this with sorting
            if after and sort_by != 'id':
                # For non-id sorting, we need to use offset-based pagination
                try:
                    offset = int(after)
                    items = list(qs[offset:offset + first + 1])
                    has_next_page = len(items) > first
                    if has_next_page:
                        items = items[:first]
                    
                    has_previous_page = offset > 0
                    start_cursor = str(offset) if items else None
                    end_cursor = str(offset + len(items)) if items else None
                except (ValueError, TypeError):
                    offset = 0
                    items = list(qs[:first + 1])
                    has_next_page = len(items) > first
                    if has_next_page:
                        items = items[:first]
                    has_previous_page = False
                    start_cursor = "0" if items else None
                    end_cursor = str(len(items)) if items else None
            else:
                # For id-based sorting or first page, use cursor pagination
                start_id = 0
                if after and sort_by in [None, 'id']:
                    try:
                        start_id = int(after)
                    except (ValueError, TypeError):
                        start_id = 0
                
                if sort_by in [None, 'id'] and sort_direction != 'desc':
                    filtered_qs = qs.filter(id__gt=start_id)
                else:
                    # Use offset for other sorts
                    offset = int(after) if after else 0
                    filtered_qs = qs[offset:]
                
                items = list(filtered_qs[:first + 1])
                
                has_next_page = len(items) > first
                if has_next_page:
                    items = items[:first]
                
                has_previous_page = start_id > 0 if sort_by in [None, 'id'] else int(after or 0) > 0
                
                if sort_by in [None, 'id'] and sort_direction != 'desc':
                    start_cursor = str(items[0].id) if items else None
                    end_cursor = str(items[-1].id) if items else None
                else:
                    offset = int(after) if after else 0
                    start_cursor = str(offset) if items else None
                    end_cursor = str(offset + len(items)) if items else None
            
            return {
                'items': items,
                'total_count': total_count,
                'has_next_page': has_next_page,
                'has_previous_page': has_previous_page,
                'start_cursor': start_cursor,
                'end_cursor': end_cursor
            }

        result = await get_artists_page()
        
        return ArtistsConnection(
            edges=[Artist.from_django(artist) for artist in result['items']],
            page_info=PageInfo(
                has_next_page=result['has_next_page'],
                has_previous_page=result['has_previous_page'],
                start_cursor=result['start_cursor'],
                end_cursor=result['end_cursor']
            ),
            total_count=result['total_count']
        )

    @strawberry.field
    async def albums(
        self,
        artist_id: Optional[int] = None,
        wanted: Optional[bool] = None,
        downloaded: Optional[bool] = None,
        first: int = 20,
        after: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_direction: Optional[str] = None
    ) -> AlbumsConnection:
        @sync_to_async
        def get_albums_page():
            # Build base queryset
            qs = DjangoAlbum.objects.all()
            if artist_id:
                # Get the artist's GID from the ID
                try:
                    artist = DjangoArtist.objects.get(id=artist_id)
                    qs = qs.filter(artist=artist.gid)
                except DjangoArtist.DoesNotExist:
                    return {
                        'items': [],
                        'total_count': 0,
                        'has_next_page': False,
                        'has_previous_page': False,
                        'start_cursor': None,
                        'end_cursor': None
                    }
            if wanted is not None:
                qs = qs.filter(wanted=wanted)
            if downloaded is not None:
                qs = qs.filter(downloaded=downloaded)

            # Apply sorting
            sort_field = 'id'  # default
            if sort_by == 'name':
                sort_field = 'name'
            elif sort_by == 'wanted':
                sort_field = 'wanted'
            elif sort_by == 'downloaded':
                sort_field = 'downloaded'
            elif sort_by == 'album_type':
                sort_field = 'album_type'

            # Apply sort direction
            if sort_direction == 'desc':
                sort_field = f'-{sort_field}'

            qs = qs.order_by(sort_field, 'id')  # Always include id for consistent pagination

            # Get total count
            total_count = qs.count()

            # Handle cursor pagination
            if after and sort_by != 'id':
                # For non-id sorting, use offset-based pagination
                try:
                    offset = int(after)
                    items = list(qs[offset:offset + first + 1])
                    has_next_page = len(items) > first
                    if has_next_page:
                        items = items[:first]

                    has_previous_page = offset > 0
                    start_cursor = str(offset) if items else None
                    end_cursor = str(offset + len(items)) if items else None
                except (ValueError, TypeError):
                    offset = 0
                    items = list(qs[:first + 1])
                    has_next_page = len(items) > first
                    if has_next_page:
                        items = items[:first]
                    has_previous_page = False
                    start_cursor = "0" if items else None
                    end_cursor = str(len(items)) if items else None
            else:
                # For id-based sorting or first page, use cursor pagination
                start_id = 0
                if after and sort_by in [None, 'id']:
                    try:
                        start_id = int(after)
                    except (ValueError, TypeError):
                        start_id = 0

                if sort_by in [None, 'id'] and sort_direction != 'desc':
                    filtered_qs = qs.filter(id__gt=start_id)
                else:
                    # Use offset for other sorts
                    offset = int(after) if after else 0
                    filtered_qs = qs[offset:]

                items = list(filtered_qs[:first + 1])

                has_next_page = len(items) > first
                if has_next_page:
                    items = items[:first]

                has_previous_page = start_id > 0 if sort_by in [None, 'id'] else int(after or 0) > 0

                if sort_by in [None, 'id'] and sort_direction != 'desc':
                    start_cursor = str(items[0].id) if items else None
                    end_cursor = str(items[-1].id) if items else None
                else:
                    offset = int(after) if after else 0
                    start_cursor = str(offset) if items else None
                    end_cursor = str(offset + len(items)) if items else None

            return {
                'items': items,
                'total_count': total_count,
                'has_next_page': has_next_page,
                'has_previous_page': has_previous_page,
                'start_cursor': start_cursor,
                'end_cursor': end_cursor
            }

        result = await get_albums_page()

        # Populate artist names for albums
        @sync_to_async
        def get_artist_names(albums):
            artist_gids = {album.artist for album in albums if album.artist}
            artists = {artist.gid: artist.name for artist in DjangoArtist.objects.filter(gid__in=artist_gids)}
            return artists

        artist_names = await get_artist_names(result['items'])

        return AlbumsConnection(
            edges=[Album(
                id=album.id,
                spotify_gid=album.spotify_gid or "",
                spotify_uri=album.spotify_uri or "",
                name=album.name,
                total_tracks=album.total_tracks or 0,
                downloaded=album.downloaded,
                wanted=album.wanted,
                album_type=album.album_type,
                album_group=album.album_group,
                artist=artist_names.get(album.artist)
            ) for album in result['items']],
            page_info=PageInfo(
                has_next_page=result['has_next_page'],
                has_previous_page=result['has_previous_page'],
                start_cursor=result['start_cursor'],
                end_cursor=result['end_cursor']
            ),
            total_count=result['total_count']
        )

    @strawberry.field
    async def songs(
        self, 
        artist_id: Optional[int] = None, 
        first: int = 20,
        after: Optional[str] = None
    ) -> SongsConnection:
        @sync_to_async
        def get_songs_page():
            qs = DjangoSong.objects.all().order_by('id')
            if artist_id:
                qs = qs.filter(primary_artist_id=artist_id)
            
            total_count = qs.count()
            
            start_id = 0
            if after:
                try:
                    start_id = int(after)
                except (ValueError, TypeError):
                    start_id = 0
            
            filtered_qs = qs.filter(id__gt=start_id)
            items = list(filtered_qs[:first + 1])
            
            has_next_page = len(items) > first
            if has_next_page:
                items = items[:first]
            
            has_previous_page = start_id > 0
            start_cursor = str(items[0].id) if items else None
            end_cursor = str(items[-1].id) if items else None
            
            return {
                'items': items,
                'total_count': total_count,
                'has_next_page': has_next_page,
                'has_previous_page': has_previous_page,
                'start_cursor': start_cursor,
                'end_cursor': end_cursor
            }

        result = await get_songs_page()
        
        return SongsConnection(
            edges=[Song.from_django(song) for song in result['items']],
            page_info=PageInfo(
                has_next_page=result['has_next_page'],
                has_previous_page=result['has_previous_page'],
                start_cursor=result['start_cursor'],
                end_cursor=result['end_cursor']
            ),
            total_count=result['total_count']
        )

    @strawberry.field
    async def playlists(
        self,
        enabled: Optional[bool] = None,
        first: int = 20,
        after: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_direction: Optional[str] = None
    ) -> PlaylistsConnection:
        @sync_to_async
        def get_playlists_page():
            # Build base queryset
            qs = DjangoTrackedPlaylist.objects.all()
            if enabled is not None:
                qs = qs.filter(enabled=enabled)

            # Apply sorting
            sort_field = 'id'  # default
            if sort_by == 'name':
                sort_field = 'name'
            elif sort_by == 'enabled':
                sort_field = 'enabled'
            elif sort_by == 'auto_track_artists':
                sort_field = 'auto_track_artists'
            elif sort_by == 'last_synced_at':
                sort_field = 'last_synced_at'

            # Apply sort direction
            if sort_direction == 'desc':
                sort_field = f'-{sort_field}'

            qs = qs.order_by(sort_field, 'id')  # Always include id for consistent pagination

            # Get total count
            total_count = qs.count()

            # Handle cursor pagination
            if after and sort_by != 'id':
                # For non-id sorting, use offset-based pagination
                try:
                    offset = int(after)
                    items = list(qs[offset:offset + first + 1])
                    has_next_page = len(items) > first
                    if has_next_page:
                        items = items[:first]

                    has_previous_page = offset > 0
                    start_cursor = str(offset) if items else None
                    end_cursor = str(offset + len(items)) if items else None
                except (ValueError, TypeError):
                    offset = 0
                    items = list(qs[:first + 1])
                    has_next_page = len(items) > first
                    if has_next_page:
                        items = items[:first]
                    has_previous_page = False
                    start_cursor = "0" if items else None
                    end_cursor = str(len(items)) if items else None
            else:
                # For id-based sorting or first page, use cursor pagination
                start_id = 0
                if after and sort_by in [None, 'id']:
                    try:
                        start_id = int(after)
                    except (ValueError, TypeError):
                        start_id = 0

                if sort_by in [None, 'id'] and sort_direction != 'desc':
                    filtered_qs = qs.filter(id__gt=start_id)
                else:
                    # Use offset for other sorts
                    offset = int(after) if after else 0
                    filtered_qs = qs[offset:]

                items = list(filtered_qs[:first + 1])

                has_next_page = len(items) > first
                if has_next_page:
                    items = items[:first]

                has_previous_page = start_id > 0 if sort_by in [None, 'id'] else int(after or 0) > 0

                if sort_by in [None, 'id'] and sort_direction != 'desc':
                    start_cursor = str(items[0].id) if items else None
                    end_cursor = str(items[-1].id) if items else None
                else:
                    offset = int(after) if after else 0
                    start_cursor = str(offset) if items else None
                    end_cursor = str(offset + len(items)) if items else None

            return {
                'items': items,
                'total_count': total_count,
                'has_next_page': has_next_page,
                'has_previous_page': has_previous_page,
                'start_cursor': start_cursor,
                'end_cursor': end_cursor
            }

        result = await get_playlists_page()

        return PlaylistsConnection(
            edges=[TrackedPlaylist.from_django(playlist) for playlist in result['items']],
            page_info=PageInfo(
                has_next_page=result['has_next_page'],
                has_previous_page=result['has_previous_page'],
                start_cursor=result['start_cursor'],
                end_cursor=result['end_cursor']
            ),
            total_count=result['total_count']
        )

@strawberry.type
class Mutation:
    @strawberry.field
    async def track_artist(self, artist_id: int) -> MutationResult:
        @sync_to_async
        def update_artist():
            try:
                artist = DjangoArtist.objects.get(id=artist_id)
                artist.tracked = True
                artist.save()
                return artist, None
            except DjangoArtist.DoesNotExist:
                return None, "Artist not found"
            except Exception as e:
                return None, f"Error tracking artist: {str(e)}"

        django_artist, error = await update_artist()
        if error:
            return MutationResult(success=False, message=error)
        
        return MutationResult(
            success=True,
            message="Artist tracked successfully",
            artist=Artist.from_django(django_artist)
        )

    @strawberry.field
    async def untrack_artist(self, artist_id: int) -> MutationResult:
        @sync_to_async
        def update_artist():
            try:
                artist = DjangoArtist.objects.get(id=artist_id)
                artist.tracked = False
                artist.save()
                return artist, None
            except DjangoArtist.DoesNotExist:
                return None, "Artist not found"
            except Exception as e:
                return None, f"Error untracking artist: {str(e)}"

        django_artist, error = await update_artist()
        if error:
            return MutationResult(success=False, message=error)
        
        return MutationResult(
            success=True,
            message="Artist untracked successfully",
            artist=Artist.from_django(django_artist)
        )

    @strawberry.field
    async def set_album_wanted(self, album_id: int, wanted: bool) -> MutationResult:
        @sync_to_async
        def update_album():
            try:
                album = DjangoAlbum.objects.get(id=album_id)
                album.wanted = wanted
                album.save()
                return album, None
            except DjangoAlbum.DoesNotExist:
                return None, "Album not found"
            except Exception as e:
                return None, f"Error updating album: {str(e)}"

        django_album, error = await update_album()
        if error:
            return MutationResult(success=False, message=error)
        
        return MutationResult(
            success=True,
            message=f"Album marked as {'wanted' if wanted else 'unwanted'}",
            album=Album.from_django(django_album)
        )

    @strawberry.field
    async def toggle_playlist(self, playlist_id: int) -> MutationResult:
        @sync_to_async
        def update_playlist():
            try:
                playlist = DjangoTrackedPlaylist.objects.get(id=playlist_id)
                playlist.enabled = not playlist.enabled
                playlist.save()
                return playlist, None
            except DjangoTrackedPlaylist.DoesNotExist:
                return None, "Playlist not found"
            except Exception as e:
                return None, f"Error updating playlist: {str(e)}"

        django_playlist, error = await update_playlist()
        if error:
            return MutationResult(success=False, message=error)
        
        return MutationResult(
            success=True,
            message=f"Playlist {'enabled' if django_playlist.enabled else 'disabled'}",
            playlist=TrackedPlaylist.from_django(django_playlist)
        )

    @strawberry.field
    async def sync_artist(self, artist_id: int) -> TaskResult:
        @sync_to_async
        def start_sync_task():
            try:
                from library_manager.tasks import sync_artist_task
                artist = DjangoArtist.objects.get(id=artist_id)
                task = sync_artist_task(artist.gid)
                return str(task.id), None
            except DjangoArtist.DoesNotExist:
                return None, "Artist not found"
            except Exception as e:
                return None, f"Error starting sync task: {str(e)}"

        task_id, error = await start_sync_task()
        if error:
            return TaskResult(success=False, message=error)
        
        return TaskResult(
            success=True,
            message="Artist sync task started",
            task_id=task_id
        )

schema = strawberry.Schema(query=Query, mutation=Mutation) 