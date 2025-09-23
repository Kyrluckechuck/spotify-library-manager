from enum import Enum
from typing import List, Optional

import strawberry

from .scalars import DateTime


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
    TRACK = "TRACK"


@strawberry.type
class Artist:
    id: int
    name: str
    gid: str
    spotify_uri: str
    is_tracked: bool
    last_synced: Optional[DateTime]
    added_at: Optional[DateTime] = None


@strawberry.type
class Album:
    id: int
    name: str
    spotify_gid: str
    total_tracks: int
    wanted: bool
    downloaded: bool
    album_type: Optional[str]
    album_group: Optional[str]
    artist: Optional[str]
    artist_id: Optional[int]


@strawberry.type
class Song:
    id: int
    name: str
    gid: str
    primary_artist: str
    primary_artist_id: int
    created_at: DateTime
    failed_count: int
    bitrate: int
    unavailable: bool
    file_path: Optional[str]
    downloaded: bool
    spotify_uri: str


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
    id: int
    name: str
    url: str
    enabled: bool
    auto_track_artists: bool
    last_synced_at: Optional[DateTime]


@strawberry.type
class DownloadProgress:
    entity_id: str
    entity_type: str
    progress: float
    status: DownloadStatus
    message: Optional[str]


@strawberry.type
class DownloadHistory:
    id: str
    entity_id: str
    entity_type: str  # "TRACK" | "ALBUM" | "PLAYLIST"
    status: DownloadStatus
    started_at: DateTime
    completed_at: Optional[DateTime]
    error_message: Optional[str]


@strawberry.type
class TaskHistory:
    id: str
    task_id: str
    type: TaskType
    entity_id: str
    entity_type: EntityType
    status: TaskStatus
    started_at: DateTime
    completed_at: Optional[DateTime]
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
    edges: List[Artist]
    page_info: PageInfo
    total_count: int


@strawberry.type
class AlbumConnection:
    edges: List[Album]
    page_info: PageInfo
    total_count: int


@strawberry.type
class PlaylistConnection:
    edges: List[Playlist]
    page_info: PageInfo
    total_count: int


@strawberry.type
class SongConnection:
    edges: List[Song]
    page_info: PageInfo
    total_count: int


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


@strawberry.type
class MutationResult:
    success: bool
    message: str
    artist: Optional[Artist] = None
    album: Optional[Album] = None
    playlist: Optional[Playlist] = None


@strawberry.input
class UpdatePlaylistInput:
    playlist_id: str
    is_tracked: Optional[bool] = None
    auto_track_artists: Optional[bool] = None


@strawberry.type
class PendingTask:
    id: str
    name: str
    args: List[str]
    kwargs: dict
    priority: Optional[int]
    created_at: Optional[str]


@strawberry.type
class TaskCount:
    task_name: str
    count: int


@strawberry.type
class QueueStatus:
    total_pending_tasks: int
    task_counts: List[TaskCount]
    queue_size: int
