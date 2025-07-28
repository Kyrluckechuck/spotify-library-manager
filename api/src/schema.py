from typing import List, Optional
import strawberry
from asgiref.sync import sync_to_async
from library_manager.models import Artist as DjangoArtist
from library_manager.models import Album as DjangoAlbum
from library_manager.models import Song as DjangoSong
from library_manager.models import TrackedPlaylist as DjangoTrackedPlaylist
from library_manager.models import TaskHistory as DjangoTaskHistory
from library_manager.validation import validate_spotify_url

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
    artist_id: Optional[int] = None  # Artist ID for navigation

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
            artist_id=None,  # Will be populated in the resolver
        )

@strawberry.type
class Song:
    id: int
    name: str
    gid: str
    created_at: str
    failed_count: int
    bitrate: Optional[int]
    unavailable: bool
    file_path: Optional[str]
    downloaded: bool
    spotify_uri: str
    artist: Optional[str]  # Add artist field

    @classmethod
    def from_django(cls, django_song: DjangoSong, artist_name: Optional[str] = None) -> "Song":
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
            artist=artist_name
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
class LogMessage:
    timestamp: str
    message: str

@strawberry.type
class CleanupResult:
    success: bool
    message: str
    cleaned_count: int

@strawberry.type
class TaskHistory:
    id: str
    task_id: str
    type: str
    entity_id: str
    entity_type: str
    status: str
    started_at: str
    completed_at: Optional[str]
    error_message: Optional[str]
    duration_seconds: Optional[int]
    progress_percentage: float
    log_messages: List[LogMessage]

    @classmethod
    def from_django(cls, django_task: DjangoTaskHistory) -> "TaskHistory":
        return cls(
            id=str(django_task.id),
            task_id=django_task.task_id,
            type=django_task.type,
            entity_id=django_task.entity_id,
            entity_type=django_task.entity_type,
            status=django_task.status,
            started_at=django_task.started_at.isoformat(),
            completed_at=django_task.completed_at.isoformat() if django_task.completed_at else None,
            error_message=django_task.error_message,
            duration_seconds=django_task.duration_seconds,
            progress_percentage=django_task.progress_percentage,
            log_messages=[LogMessage(timestamp=log['timestamp'], message=log['message']) for log in django_task.log_messages] if django_task.log_messages else []
        )

@strawberry.type
class TaskHistoryConnection:
    edges: List[TaskHistory]
    page_info: PageInfo
    total_count: int

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
        sort_direction: Optional[str] = None,
        search: Optional[str] = None
    ) -> ArtistsConnection:
        @sync_to_async
        def get_artists_page():
            # Build base queryset
            qs = DjangoArtist.objects.all()
            
            # Apply filters
            if tracked is not None:
                qs = qs.filter(tracked=tracked)
            
            # Apply search
            if search:
                qs = qs.filter(name__icontains=search)

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
        sort_direction: Optional[str] = None,
        search: Optional[str] = None
    ) -> AlbumsConnection:
        @sync_to_async
        def get_albums_page():
            # Build base queryset
            qs = DjangoAlbum.objects.all()
            
            # Apply filters
            if artist_id:
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
            
            # Apply search
            if search:
                qs = qs.filter(name__icontains=search)

            # Apply sorting
            sort_field = 'id'  # default
            if sort_by == 'name':
                sort_field = 'name'
            elif sort_by == 'artist':
                sort_field = 'artist'
            elif sort_by == 'downloaded':
                sort_field = 'downloaded'
            elif sort_by == 'wanted':
                sort_field = 'wanted'
            elif sort_by == 'total_tracks':
                sort_field = 'total_tracks'
            elif sort_by == 'created_at':
                sort_field = 'id'  # Use id as proxy for created_at

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

        # Populate artist names and IDs for albums
        @sync_to_async
        def get_artist_data(albums):
            # Get unique artist GIDs from albums
            artist_gids = {album.artist.gid for album in albums if album.artist}
            artists = DjangoArtist.objects.filter(gid__in=list(artist_gids))
            artist_names = {artist.gid: artist.name for artist in artists}
            artist_ids = {artist.gid: artist.id for artist in artists}
            return artist_names, artist_ids

        artist_names, artist_ids = await get_artist_data(result['items'])

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
                artist=artist_names.get(album.artist.gid),
                artist_id=artist_ids.get(album.artist.gid)
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
        downloaded: Optional[bool] = None,
        unavailable: Optional[bool] = None,
        first: int = 20,
        after: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_direction: Optional[str] = None,
        search: Optional[str] = None
    ) -> SongsConnection:
        @sync_to_async
        def get_songs_page():
            # Build base queryset
            qs = DjangoSong.objects.all()
            
            # Apply filters
            if artist_id:
                qs = qs.filter(primary_artist_id=artist_id)
            if downloaded is not None:
                qs = qs.filter(downloaded=downloaded)
            if unavailable is not None:
                qs = qs.filter(unavailable=unavailable)
            
            # Apply search
            if search:
                qs = qs.filter(name__icontains=search)

            # Apply sorting
            sort_field = 'id'  # default
            if sort_by == 'name':
                sort_field = 'name'
            elif sort_by == 'artist':
                sort_field = 'primary_artist__name'  # Sort by artist name
            elif sort_by == 'downloaded':
                sort_field = 'downloaded'
            elif sort_by == 'unavailable':
                sort_field = 'unavailable'
            elif sort_by == 'created_at':
                sort_field = 'created_at'

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

        result = await get_songs_page()

        # Populate artist names for songs
        @sync_to_async
        def get_artist_names(songs):
            artist_ids = {song.primary_artist_id for song in songs}
            artists = {artist.id: artist.name for artist in DjangoArtist.objects.filter(id__in=artist_ids)}
            return artists

        artist_names = await get_artist_names(result['items'])

        return SongsConnection(
            edges=[Song.from_django(song, artist_names.get(song.primary_artist_id)) for song in result['items']],
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
        sort_direction: Optional[str] = None,
        search: Optional[str] = None
    ) -> PlaylistsConnection:
        @sync_to_async
        def get_playlists_page():
            # Build base queryset
            qs = DjangoTrackedPlaylist.objects.all()
            
            # Apply filters
            if enabled is not None:
                qs = qs.filter(enabled=enabled)
            
            # Apply search
            if search:
                qs = qs.filter(name__icontains=search)

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

    @strawberry.field
    async def artist(self, id: int) -> Optional[Artist]:
        @sync_to_async
        def get_artist():
            try:
                return DjangoArtist.objects.get(id=id)
            except DjangoArtist.DoesNotExist:
                return None
        
        artist = await get_artist()
        return Artist.from_django(artist) if artist else None

    @strawberry.field
    async def active_tasks(
        self,
        first: int = 20,
        after: Optional[str] = None
    ) -> TaskHistoryConnection:
        @sync_to_async
        def get_active_tasks():
            # Get tasks that are currently running
            queryset = DjangoTaskHistory.objects.filter(status='RUNNING')

            # Apply cursor-based pagination
            if after:
                try:
                    after_id = int(after)
                    queryset = queryset.filter(id__gt=after_id)
                except (ValueError, TypeError):
                    pass

            # Get total count
            total_count = queryset.count()

            # Get items with pagination
            items = list(queryset.order_by('-started_at')[:first + 1])
            has_next_page = len(items) > first
            items = items[:first]

            # Convert to GraphQL types
            task_histories = [TaskHistory.from_django(item) for item in items]

            return {
                'edges': task_histories,
                'page_info': {
                    'has_next_page': has_next_page,
                    'has_previous_page': after is not None,
                    'start_cursor': str(items[0].id) if items else None,
                    'end_cursor': str(items[-1].id) if items else None,
                },
                'total_count': total_count
            }

        result = await get_active_tasks()
        
        return TaskHistoryConnection(
            edges=result['edges'],
            page_info=PageInfo(**result['page_info']),
            total_count=result['total_count']
        )

    @strawberry.field
    async def task_history(
        self,
        first: int = 20,
        after: Optional[str] = None,
        status: Optional[str] = None,
        type: Optional[str] = None,
        entity_type: Optional[str] = None,
        search: Optional[str] = None
    ) -> TaskHistoryConnection:
        @sync_to_async
        def get_task_history():
            from django.db import models
            
            queryset = DjangoTaskHistory.objects.all()

            # Apply filters
            if status:
                queryset = queryset.filter(status=status)
            if type:
                queryset = queryset.filter(type=type)
            if entity_type:
                queryset = queryset.filter(entity_type=entity_type)
            if search:
                queryset = queryset.filter(
                    models.Q(task_id__icontains=search) |
                    models.Q(entity_id__icontains=search)
                )

            # Apply cursor-based pagination
            if after:
                try:
                    after_id = int(after)
                    queryset = queryset.filter(id__gt=after_id)
                except (ValueError, TypeError):
                    pass

            # Get total count
            total_count = queryset.count()

            # Get items with pagination
            items = list(queryset.order_by('-started_at')[:first + 1])
            has_next_page = len(items) > first
            items = items[:first]

            # Convert to GraphQL types
            task_histories = [TaskHistory.from_django(item) for item in items]

            return {
                'edges': task_histories,
                'page_info': {
                    'has_next_page': has_next_page,
                    'has_previous_page': after is not None,
                    'start_cursor': str(items[0].id) if items else None,
                    'end_cursor': str(items[-1].id) if items else None,
                },
                'total_count': total_count
            }

        result = await get_task_history()
        
        return TaskHistoryConnection(
            edges=result['edges'],
            page_info=PageInfo(**result['page_info']),
            total_count=result['total_count']
        )

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def track_artist(self, artist_id: int) -> MutationResult:
        @sync_to_async
        def track_artist_sync():
            try:
                artist = DjangoArtist.objects.get(id=artist_id)
                artist.tracked = True
                artist.save()
                return MutationResult(
                    success=True,
                    message=f"Artist '{artist.name}' is now being tracked",
                    artist=Artist.from_django(artist)
                )
            except DjangoArtist.DoesNotExist:
                return MutationResult(
                    success=False,
                    message=f"Artist with ID {artist_id} not found"
                )
        
        return await track_artist_sync()

    @strawberry.mutation
    async def untrack_artist(self, artist_id: int) -> MutationResult:
        @sync_to_async
        def untrack_artist_sync():
            try:
                artist = DjangoArtist.objects.get(id=artist_id)
                artist.tracked = False
                artist.save()
                return MutationResult(
                    success=True,
                    message=f"Artist '{artist.name}' is no longer being tracked",
                    artist=Artist.from_django(artist)
                )
            except DjangoArtist.DoesNotExist:
                return MutationResult(
                    success=False,
                    message=f"Artist with ID {artist_id} not found"
                )
        
        return await untrack_artist_sync()

    @strawberry.mutation
    async def sync_artist(self, artist_id: int) -> TaskResult:
        @sync_to_async
        def sync_artist_sync():
            try:
                artist = DjangoArtist.objects.get(id=artist_id)
                # Import the task here to avoid circular imports
                from library_manager.tasks import fetch_all_albums_for_artist
                task = fetch_all_albums_for_artist(artist_id)
                return TaskResult(
                    success=True,
                    message=f"Started syncing artist '{artist.name}'",
                    task_id=str(task.id)
                )
            except DjangoArtist.DoesNotExist:
                return TaskResult(
                    success=False,
                    message=f"Artist with ID {artist_id} not found"
                )
        
        return await sync_artist_sync()

    @strawberry.mutation
    async def sync_playlist(self, playlist_id: int) -> TaskResult:
        @sync_to_async
        def sync_playlist_sync():
            try:
                playlist = DjangoTrackedPlaylist.objects.get(id=playlist_id)
                # Import the task here to avoid circular imports
                from library_manager.tasks import _sync_tracked_playlist_internal
                task_history = _sync_tracked_playlist_internal(playlist)
                return TaskResult(
                    success=True,
                    message=f"Started syncing playlist '{playlist.name}'",
                    task_id=str(task_history.id) if task_history else None
                )
            except DjangoTrackedPlaylist.DoesNotExist:
                return TaskResult(
                    success=False,
                    message=f"Playlist with ID {playlist_id} not found"
                )
            except Exception as e:
                import logging
                logger = logging.getLogger('library_manager')
                logger.error(f"Error in sync_playlist mutation: {e}", exc_info=True)
                return TaskResult(
                    success=False,
                    message=f"Failed to sync playlist: {str(e)}"
                )
        
        return await sync_playlist_sync()

    @strawberry.mutation
    async def cleanup_stuck_tasks(self) -> CleanupResult:
        """Clean up stuck tasks that have exceeded their timeout"""
        @sync_to_async
        def cleanup():
            from library_manager.models import TaskHistory
            return TaskHistory.cleanup_stuck_tasks()
        
        try:
            cleaned_count = await cleanup()
            return CleanupResult(
                success=True,
                message=f"Cleaned up {cleaned_count} stuck task(s)",
                cleaned_count=cleaned_count
            )
        except Exception as e:
            return CleanupResult(
                success=False,
                message=f"Error cleaning up stuck tasks: {str(e)}",
                cleaned_count=0
            )

    @strawberry.mutation
    async def download_url(self, url: str, auto_track_artists: bool = False) -> TaskResult:
        @sync_to_async
        def download_url_sync():
            try:
                # Validate Spotify URL
                is_valid, error_message = validate_spotify_url(url)
                if not is_valid:
                    return TaskResult(
                        success=False,
                        message=error_message
                    )
                
                # Import the task here to avoid circular imports
                from library_manager.tasks import download_playlist
                task = download_playlist(url, tracked=auto_track_artists)
                return TaskResult(
                    success=True,
                    message=f"Started downloading from URL: {url}",
                    task_id=str(task.id)
                )
            except Exception as e:
                return TaskResult(
                    success=False,
                    message=f"Failed to start download: {str(e)}"
                )
        
        return await download_url_sync()

    @strawberry.mutation
    async def create_playlist(self, url: str, name: str, auto_track_artists: bool = False) -> MutationResult:
        @sync_to_async
        def create_playlist_sync():
            try:
                # Validate Spotify URL
                is_valid, error_message = validate_spotify_url(url)
                if not is_valid:
                    return MutationResult(
                        success=False,
                        message=error_message
                    )
                
                # Import the task here to avoid circular imports
                from library_manager.tasks import download_playlist
                
                # Create the playlist record
                playlist = DjangoTrackedPlaylist.objects.create(
                    name=name,
                    url=url,
                    enabled=True,
                    auto_track_artists=auto_track_artists
                )
                
                # Start the download task
                download_playlist(url, tracked=auto_track_artists)
                
                return MutationResult(
                    success=True,
                    message=f"Created playlist '{name}' and started download",
                    playlist=TrackedPlaylist.from_django(playlist)
                )
            except Exception as e:
                return MutationResult(
                    success=False,
                    message=f"Failed to create playlist: {str(e)}"
                )
        
        return await create_playlist_sync()

    @strawberry.mutation
    async def update_playlist(self, playlist_id: int, name: str = None, auto_track_artists: bool = None) -> MutationResult:
        @sync_to_async
        def update_playlist_sync():
            try:
                playlist = DjangoTrackedPlaylist.objects.get(id=playlist_id)
                
                if name is not None:
                    playlist.name = name
                if auto_track_artists is not None:
                    playlist.auto_track_artists = auto_track_artists
                
                playlist.save()
                
                return MutationResult(
                    success=True,
                    message=f"Updated playlist '{playlist.name}'",
                    playlist=TrackedPlaylist.from_django(playlist)
                )
            except DjangoTrackedPlaylist.DoesNotExist:
                return MutationResult(
                    success=False,
                    message=f"Playlist with ID {playlist_id} not found"
                )
            except Exception as e:
                return MutationResult(
                    success=False,
                    message=f"Failed to update playlist: {str(e)}"
                )
        
        return await update_playlist_sync()

    @strawberry.mutation
    async def set_album_wanted(self, album_id: int, wanted: bool) -> MutationResult:
        @sync_to_async
        def set_album_wanted_sync():
            try:
                album = DjangoAlbum.objects.get(id=album_id)
                album.wanted = wanted
                album.save()
                return MutationResult(
                    success=True,
                    message=f"Album '{album.name}' {'wanted' if wanted else 'not wanted'}",
                    album=Album.from_django(album)
                )
            except DjangoAlbum.DoesNotExist:
                return MutationResult(
                    success=False,
                    message=f"Album with ID {album_id} not found"
                )
        
        return await set_album_wanted_sync()

    @strawberry.mutation
    async def toggle_playlist(self, playlist_id: int) -> MutationResult:
        @sync_to_async
        def toggle_playlist_sync():
            try:
                playlist = DjangoTrackedPlaylist.objects.get(id=playlist_id)
                playlist.enabled = not playlist.enabled
                playlist.save()
                return MutationResult(
                    success=True,
                    message=f"Playlist '{playlist.name}' {'enabled' if playlist.enabled else 'disabled'}",
                    playlist=TrackedPlaylist.from_django(playlist)
                )
            except DjangoTrackedPlaylist.DoesNotExist:
                return MutationResult(
                    success=False,
                    message=f"Playlist with ID {playlist_id} not found"
                )
        
        return await toggle_playlist_sync()

    @strawberry.mutation
    async def retry_all_missing_known_songs(self) -> TaskResult:
        @sync_to_async
        def retry_all_missing_known_songs_sync():
            try:
                from library_manager.tasks import retry_all_missing_known_songs
                task = retry_all_missing_known_songs()
                return TaskResult(
                    success=True,
                    message="Started retry of all missing known songs",
                    task_id=str(task.id) if task else None
                )
            except Exception as e:
                return TaskResult(
                    success=False,
                    message=f"Failed to start retry: {str(e)}"
                )
        
        return await retry_all_missing_known_songs_sync()

    @strawberry.mutation
    async def validate_undownloaded_songs(self) -> TaskResult:
        @sync_to_async
        def validate_undownloaded_songs_sync():
            try:
                from library_manager.tasks import validate_undownloaded_songs
                task = validate_undownloaded_songs()
                return TaskResult(
                    success=True,
                    message="Started validation of undownloaded songs",
                    task_id=str(task.id) if task else None
                )
            except Exception as e:
                return TaskResult(
                    success=False,
                    message=f"Failed to start validation: {str(e)}"
                )
        
        return await validate_undownloaded_songs_sync()

    @strawberry.mutation
    async def download_all_for_tracked_artists(self) -> TaskResult:
        @sync_to_async
        def download_all_for_tracked_artists_sync():
            try:
                from library_manager.tasks import download_missing_tracked_artists
                task = download_missing_tracked_artists()
                return TaskResult(
                    success=True,
                    message="Started download for all tracked artists",
                    task_id=str(task.id) if task else None
                )
            except Exception as e:
                return TaskResult(
                    success=False,
                    message=f"Failed to start download: {str(e)}"
                )
        
        return await download_all_for_tracked_artists_sync()

    @strawberry.mutation
    async def fetch_all_for_tracked_artists(self) -> TaskResult:
        @sync_to_async
        def fetch_all_for_tracked_artists_sync():
            try:
                from library_manager.tasks import update_tracked_artists
                task = update_tracked_artists()
                return TaskResult(
                    success=True,
                    message="Started fetch for all tracked artists",
                    task_id=str(task.id) if task else None
                )
            except Exception as e:
                return TaskResult(
                    success=False,
                    message=f"Failed to start fetch: {str(e)}"
                )
        
        return await fetch_all_for_tracked_artists_sync()

schema = strawberry.Schema(query=Query, mutation=Mutation) 