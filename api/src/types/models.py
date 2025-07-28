from typing import List, Optional
from datetime import datetime
import strawberry
from enum import Enum

@strawberry.enum
class DownloadStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

@strawberry.enum
class TaskStatus(Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PENDING = "PENDING"

@strawberry.enum
class TaskType(Enum):
    SYNC = "SYNC"
    DOWNLOAD = "DOWNLOAD"
    FETCH = "FETCH"

@strawberry.enum
class EntityType(Enum):
    ARTIST = "ARTIST"
    ALBUM = "ALBUM"
    PLAYLIST = "PLAYLIST"

@strawberry.type
class Artist:
    id: str
    name: str
    spotify_url: str
    image_url: Optional[str]
    is_tracked: bool
    last_synced: Optional[datetime]
    auto_download: bool = False

@strawberry.type
class Album:
    id: str
    name: str
    artist_id: str
    spotify_url: str
    release_date: datetime
    image_url: Optional[str]
    is_downloaded: bool
    is_wanted: bool
    download_status: Optional[DownloadStatus]
    track_count: int

@strawberry.type
class Track:
    id: str
    name: str
    album_id: str
    artist_ids: List[str]
    duration_ms: int
    track_number: int
    disc_number: int
    spotify_url: str
    is_downloaded: bool
    download_status: Optional[DownloadStatus]

@strawberry.type
class Playlist:
    id: str
    name: str
    owner_id: str
    spotify_url: str
    image_url: Optional[str]
    track_count: int
    is_tracked: bool
    auto_track_artists: bool
    last_synced: Optional[datetime]

@strawberry.type
class DownloadHistory:
    id: str
    entity_id: str
    entity_type: str  # "TRACK" | "ALBUM" | "PLAYLIST"
    status: DownloadStatus
    started_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]

@strawberry.type
class TaskHistory:
    id: str
    task_id: str
    type: TaskType
    entity_id: str
    entity_type: EntityType
    status: TaskStatus
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[int]
    progress_percentage: Optional[float]
    log_messages: List[str]

@strawberry.type
class PageInfo:
    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[str]
    end_cursor: Optional[str]

@strawberry.type
class ArtistConnection:
    edges: List["ArtistEdge"]
    page_info: PageInfo
    total_count: int

@strawberry.type
class ArtistEdge:
    node: Artist
    cursor: str

@strawberry.type
class AlbumConnection:
    edges: List["AlbumEdge"]
    page_info: PageInfo
    total_count: int

@strawberry.type
class AlbumEdge:
    node: Album
    cursor: str

@strawberry.type
class PlaylistConnection:
    edges: List["PlaylistEdge"]
    page_info: PageInfo
    total_count: int

@strawberry.type
class PlaylistEdge:
    node: Playlist
    cursor: str

@strawberry.type
class HistoryConnection:
    edges: List["HistoryEdge"]
    page_info: PageInfo
    total_count: int

@strawberry.type
class HistoryEdge:
    node: DownloadHistory
    cursor: str

@strawberry.type
class TaskHistoryConnection:
    edges: List["TaskHistoryEdge"]
    page_info: PageInfo
    total_count: int

@strawberry.type
class TaskHistoryEdge:
    node: TaskHistory
    cursor: str

@strawberry.input
class TrackArtistInput:
    artist_id: str
    auto_download: bool = False

@strawberry.input
class TrackPlaylistInput:
    playlist_id: str
    auto_track_artists: bool = False

@strawberry.input
class UpdateArtistInput:
    artist_id: str
    is_tracked: Optional[bool] = None
    auto_download: Optional[bool] = None

@strawberry.input
class UpdateAlbumInput:
    album_id: str
    is_wanted: Optional[bool] = None

@strawberry.input
class UpdatePlaylistInput:
    playlist_id: str
    is_tracked: Optional[bool] = None
    auto_track_artists: Optional[bool] = None 