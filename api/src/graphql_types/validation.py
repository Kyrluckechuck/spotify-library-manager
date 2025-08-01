"""
Runtime type validation using Pydantic.
This module provides validation schemas for API inputs and outputs.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from .scalars import DateTime


class TaskStatus(str, Enum):
    """Task status enumeration for validation."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TaskType(str, Enum):
    """Task type enumeration for validation."""

    SYNC = "SYNC"
    DOWNLOAD = "DOWNLOAD"
    FETCH = "FETCH"


class EntityType(str, Enum):
    """Entity type enumeration for validation."""

    ARTIST = "ARTIST"
    ALBUM = "ALBUM"
    PLAYLIST = "PLAYLIST"
    TRACK = "TRACK"


class DownloadStatus(str, Enum):
    """Download status enumeration for validation."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class ArtistInput(BaseModel):
    """Validation schema for artist input data."""

    id: int = Field(..., gt=0, description="Artist ID")
    name: str = Field(..., min_length=1, max_length=500, description="Artist name")
    gid: str = Field(
        ..., min_length=1, max_length=100, description="Spotify artist GID"
    )
    tracked: bool = Field(default=False, description="Whether artist is tracked")
    added_at: Optional[DateTime] = Field(None, description="When artist was added")
    last_synced_at: Optional[DateTime] = Field(None, description="Last sync timestamp")

    @field_validator("gid")
    @classmethod
    def validate_gid(cls, v: str) -> str:
        """Validate Spotify GID format."""
        if not v.startswith("spotify:artist:"):
            raise ValueError("GID must be a valid Spotify artist URI")
        return v


class AlbumInput(BaseModel):
    """Validation schema for album input data."""

    id: int = Field(..., gt=0, description="Album ID")
    spotify_gid: str = Field(
        ..., min_length=1, max_length=100, description="Spotify album GID"
    )
    spotify_uri: str = Field(
        ..., min_length=1, max_length=100, description="Spotify album URI"
    )
    name: str = Field(..., min_length=1, max_length=500, description="Album name")
    total_tracks: int = Field(..., ge=0, description="Total number of tracks")
    downloaded: bool = Field(default=False, description="Whether album is downloaded")
    wanted: bool = Field(default=False, description="Whether album is wanted")
    album_type: Optional[str] = Field(None, max_length=50, description="Album type")
    album_group: Optional[str] = Field(None, max_length=50, description="Album group")
    artist: Optional[str] = Field(None, max_length=500, description="Artist name")
    artist_id: Optional[int] = Field(None, gt=0, description="Artist ID")

    @field_validator("spotify_gid")
    @classmethod
    def validate_spotify_gid(cls, v: str) -> str:
        """Validate Spotify GID format."""
        if not v.startswith("spotify:album:"):
            raise ValueError("GID must be a valid Spotify album URI")
        return v


class SongInput(BaseModel):
    """Validation schema for song input data."""

    id: int = Field(..., gt=0, description="Song ID")
    name: str = Field(..., min_length=1, max_length=500, description="Song name")
    gid: str = Field(..., min_length=1, max_length=100, description="Spotify song GID")
    created_at: DateTime = Field(..., description="Creation timestamp")
    failed_count: int = Field(
        ..., ge=0, description="Number of failed download attempts"
    )
    bitrate: Optional[int] = Field(None, ge=0, description="Audio bitrate")
    unavailable: bool = Field(default=False, description="Whether song is unavailable")
    file_path: Optional[str] = Field(None, max_length=1000, description="File path")
    downloaded: bool = Field(default=False, description="Whether song is downloaded")
    spotify_uri: str = Field(
        ..., min_length=1, max_length=100, description="Spotify URI"
    )
    artist: Optional[str] = Field(None, max_length=500, description="Artist name")

    @field_validator("gid")
    @classmethod
    def validate_gid(cls, v: str) -> str:
        """Validate Spotify GID format."""
        if not v.startswith("spotify:track:"):
            raise ValueError("GID must be a valid Spotify track URI")
        return v


class PlaylistInput(BaseModel):
    """Validation schema for playlist input data."""

    id: int = Field(..., gt=0, description="Playlist ID")
    name: str = Field(..., min_length=1, max_length=500, description="Playlist name")
    url: str = Field(..., min_length=1, max_length=1000, description="Playlist URL")
    enabled: bool = Field(default=False, description="Whether playlist is enabled")
    auto_track_artists: bool = Field(default=False, description="Auto-track artists")
    last_synced_at: Optional[DateTime] = Field(None, description="Last sync timestamp")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate playlist URL format."""
        if not v.startswith("https://open.spotify.com/playlist/"):
            raise ValueError("URL must be a valid Spotify playlist URL")
        return v


class TaskHistoryInput(BaseModel):
    """Validation schema for task history input data."""

    id: str = Field(..., min_length=1, max_length=100, description="Task ID")
    task_id: str = Field(
        ..., min_length=1, max_length=100, description="Internal task ID"
    )
    type: TaskType = Field(..., description="Task type")
    entity_id: str = Field(..., min_length=1, max_length=100, description="Entity ID")
    entity_type: EntityType = Field(..., description="Entity type")
    status: TaskStatus = Field(..., description="Task status")
    started_at: DateTime = Field(..., description="Start timestamp")
    completed_at: Optional[DateTime] = Field(None, description="Completion timestamp")
    error_message: Optional[str] = Field(
        None, max_length=1000, description="Error message"
    )
    duration_seconds: Optional[int] = Field(
        None, ge=0, description="Duration in seconds"
    )
    progress_percentage: float = Field(
        ..., ge=0, le=100, description="Progress percentage"
    )
    log_messages: List[str] = Field(default_factory=list, description="Log messages")


class MutationInput(BaseModel):
    """Base class for mutation inputs."""


class TrackArtistInput(MutationInput):
    """Validation schema for track artist mutation."""

    artist_id: int = Field(..., gt=0, description="Artist ID to track")
    auto_download: bool = Field(default=False, description="Auto-download albums")


class UntrackArtistInput(MutationInput):
    """Validation schema for untrack artist mutation."""

    artist_id: int = Field(..., gt=0, description="Artist ID to untrack")


class SyncArtistInput(MutationInput):
    """Validation schema for sync artist mutation."""

    artist_id: int = Field(..., gt=0, description="Artist ID to sync")


class SyncPlaylistInput(MutationInput):
    """Validation schema for sync playlist mutation."""

    playlist_id: int = Field(..., gt=0, description="Playlist ID to sync")


class SetAlbumWantedInput(MutationInput):
    """Validation schema for set album wanted mutation."""

    album_id: int = Field(..., gt=0, description="Album ID")
    wanted: bool = Field(..., description="Whether album is wanted")


class TogglePlaylistInput(MutationInput):
    """Validation schema for toggle playlist mutation."""

    playlist_id: int = Field(..., gt=0, description="Playlist ID to toggle")


class DownloadUrlInput(MutationInput):
    """Validation schema for download URL mutation."""

    url: str = Field(..., min_length=1, max_length=1000, description="URL to download")
    auto_track_artists: bool = Field(default=False, description="Auto-track artists")


class CreatePlaylistInput(MutationInput):
    """Validation schema for create playlist mutation."""

    url: str = Field(..., min_length=1, max_length=1000, description="Playlist URL")
    name: str = Field(..., min_length=1, max_length=500, description="Playlist name")
    auto_track_artists: bool = Field(default=False, description="Auto-track artists")


class UpdatePlaylistInput(MutationInput):
    """Validation schema for update playlist mutation."""

    playlist_id: int = Field(..., gt=0, description="Playlist ID")
    name: Optional[str] = Field(
        None, min_length=1, max_length=500, description="Playlist name"
    )
    auto_track_artists: Optional[bool] = Field(None, description="Auto-track artists")


class QueryInput(BaseModel):
    """Base class for query inputs."""


class ArtistsQueryInput(QueryInput):
    """Validation schema for artists query."""

    tracked: Optional[bool] = Field(None, description="Filter by tracked status")
    first: int = Field(default=20, ge=1, le=100, description="Number of items to fetch")
    after: Optional[str] = Field(None, description="Cursor for pagination")
    sort_by: Optional[str] = Field(None, max_length=50, description="Sort field")
    sort_direction: Optional[str] = Field(
        None, pattern="^(asc|desc)$", description="Sort direction"
    )
    search: Optional[str] = Field(None, max_length=200, description="Search query")

    @field_validator("sort_direction")
    @classmethod
    def validate_sort_direction(cls, v: Optional[str]) -> Optional[str]:
        """Validate sort direction."""
        if v and v not in ["asc", "desc"]:
            raise ValueError('Sort direction must be "asc" or "desc"')
        return v


class AlbumsQueryInput(QueryInput):
    """Validation schema for albums query."""

    artist_id: Optional[int] = Field(None, gt=0, description="Filter by artist ID")
    wanted: Optional[bool] = Field(None, description="Filter by wanted status")
    downloaded: Optional[bool] = Field(None, description="Filter by downloaded status")
    first: int = Field(default=20, ge=1, le=100, description="Number of items to fetch")
    after: Optional[str] = Field(None, description="Cursor for pagination")
    sort_by: Optional[str] = Field(None, max_length=50, description="Sort field")
    sort_direction: Optional[str] = Field(
        None, pattern="^(asc|desc)$", description="Sort direction"
    )
    search: Optional[str] = Field(None, max_length=200, description="Search query")


class SongsQueryInput(QueryInput):
    """Validation schema for songs query."""

    artist_id: Optional[int] = Field(None, gt=0, description="Filter by artist ID")
    downloaded: Optional[bool] = Field(None, description="Filter by downloaded status")
    unavailable: Optional[bool] = Field(
        None, description="Filter by unavailable status"
    )
    first: int = Field(default=20, ge=1, le=100, description="Number of items to fetch")
    after: Optional[str] = Field(None, description="Cursor for pagination")
    sort_by: Optional[str] = Field(None, max_length=50, description="Sort field")
    sort_direction: Optional[str] = Field(
        None, pattern="^(asc|desc)$", description="Sort direction"
    )
    search: Optional[str] = Field(None, max_length=200, description="Search query")


class PlaylistsQueryInput(QueryInput):
    """Validation schema for playlists query."""

    enabled: Optional[bool] = Field(None, description="Filter by enabled status")
    first: int = Field(default=20, ge=1, le=100, description="Number of items to fetch")
    after: Optional[str] = Field(None, description="Cursor for pagination")
    sort_by: Optional[str] = Field(None, max_length=50, description="Sort field")
    sort_direction: Optional[str] = Field(
        None, pattern="^(asc|desc)$", description="Sort direction"
    )
    search: Optional[str] = Field(None, max_length=200, description="Search query")


class TaskHistoryQueryInput(QueryInput):
    """Validation schema for task history query."""

    first: int = Field(default=20, ge=1, le=100, description="Number of items to fetch")
    after: Optional[str] = Field(None, description="Cursor for pagination")
    status: Optional[TaskStatus] = Field(None, description="Filter by status")
    type: Optional[TaskType] = Field(None, description="Filter by type")
    entity_type: Optional[EntityType] = Field(None, description="Filter by entity type")
    search: Optional[str] = Field(None, max_length=200, description="Search query")


# Utility functions for validation
def validate_artist_data(data: dict) -> ArtistInput:
    """Validate artist data using Pydantic."""
    return ArtistInput(**data)


def validate_album_data(data: dict) -> AlbumInput:
    """Validate album data using Pydantic."""
    return AlbumInput(**data)


def validate_song_data(data: dict) -> SongInput:
    """Validate song data using Pydantic."""
    return SongInput(**data)


def validate_playlist_data(data: dict) -> PlaylistInput:
    """Validate playlist data using Pydantic."""
    return PlaylistInput(**data)


def validate_task_history_data(data: dict) -> TaskHistoryInput:
    """Validate task history data using Pydantic."""
    return TaskHistoryInput(**data)
