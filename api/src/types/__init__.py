"""
Type definitions and validation for the Spotify Library Manager API.
"""

# Import specific types to avoid star import issues
from .models import (
    Artist, Album, Track, Playlist, TaskHistory, DownloadHistory,
    PageInfo, ArtistConnection, AlbumConnection, PlaylistConnection, 
    TaskHistoryConnection
)
from .django_models import (
    DjangoArtist, DjangoAlbum, DjangoSong, DjangoTrackedPlaylist, DjangoTaskHistory
)
from .validation import (
    ArtistInput, AlbumInput, SongInput, PlaylistInput, TaskHistoryInput,
    TrackArtistInput, UntrackArtistInput, SyncArtistInput, SyncPlaylistInput,
    SetAlbumWantedInput, TogglePlaylistInput, DownloadUrlInput, CreatePlaylistInput,
    UpdatePlaylistInput, ArtistsQueryInput, AlbumsQueryInput, SongsQueryInput,
    PlaylistsQueryInput, TaskHistoryQueryInput,
    validate_artist_data, validate_album_data, validate_song_data,
    validate_playlist_data, validate_task_history_data
)

__all__ = [
    # Models
    'Artist',
    'Album', 
    'Track',
    'Playlist',
    'TaskHistory',
    'DownloadHistory',
    'PageInfo',
    'ArtistConnection',
    'AlbumConnection',
    'PlaylistConnection',
    'TaskHistoryConnection',
    
    # Django model types
    'DjangoArtist',
    'DjangoAlbum',
    'DjangoSong',
    'DjangoTrackedPlaylist',
    'DjangoTaskHistory',
    
    # Validation schemas
    'ArtistInput',
    'AlbumInput',
    'SongInput',
    'PlaylistInput',
    'TaskHistoryInput',
    'TrackArtistInput',
    'UntrackArtistInput',
    'SyncArtistInput',
    'SyncPlaylistInput',
    'SetAlbumWantedInput',
    'TogglePlaylistInput',
    'DownloadUrlInput',
    'CreatePlaylistInput',
    'UpdatePlaylistInput',
    'ArtistsQueryInput',
    'AlbumsQueryInput',
    'SongsQueryInput',
    'PlaylistsQueryInput',
    'TaskHistoryQueryInput',
    
    # Validation functions
    'validate_artist_data',
    'validate_album_data',
    'validate_song_data',
    'validate_playlist_data',
    'validate_task_history_data',
] 