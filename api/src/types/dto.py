from __future__ import annotations

from typing import List, Optional, Protocol

from ..graphql_types.models import DownloadStatus, EntityType, TaskStatus, TaskType


class ArtistDTO(Protocol):
    id: int
    name: str
    gid: str
    is_tracked: bool
    last_synced: Optional[str]
    added_at: Optional[str]


class AlbumDTO(Protocol):
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


class SongDTO(Protocol):
    id: int
    name: str
    gid: str
    primary_artist: str
    primary_artist_id: int
    created_at: str
    failed_count: int
    bitrate: int
    unavailable: bool
    file_path: Optional[str]
    downloaded: bool
    spotify_uri: str


class PlaylistDTO(Protocol):
    id: int
    name: str
    url: str
    enabled: bool
    auto_track_artists: bool
    last_synced_at: Optional[str]


class DownloadHistoryDTO(Protocol):
    id: str
    entity_id: str
    entity_type: str
    status: DownloadStatus
    started_at: str
    completed_at: Optional[str]
    error_message: Optional[str]


class TaskHistoryDTO(Protocol):
    id: str
    task_id: str
    type: TaskType
    entity_id: str
    entity_type: EntityType
    status: TaskStatus
    started_at: str
    completed_at: Optional[str]
    duration_seconds: Optional[int]
    progress_percentage: Optional[float]
    log_messages: List[str]
