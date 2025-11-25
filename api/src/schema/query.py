from typing import List, Optional

import strawberry

from ..graphql_types.models import (
    Album,
    AlbumConnection,
    Artist,
    ArtistConnection,
    AuthenticationStatus,
    HistoryConnection,
    HistoryEdge,
    PageInfo,
    PeriodicTask,
    Playlist,
    PlaylistConnection,
    QueueStatus,
    Song,
    SongConnection,
    SpotifySearchAlbum,
    SpotifySearchArtist,
    SpotifySearchPlaylist,
    SpotifySearchResults,
    SpotifySearchTrack,
    SystemHealth,
    TaskCount,
    TaskHistoryConnection,
    TaskHistoryEdge,
)
from ..services import services


@strawberry.type
class Query:
    @strawberry.field
    async def artists(
        self,
        first: Optional[int] = 20,
        after: Optional[str] = None,
        is_tracked: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_direction: Optional[str] = None,
        search: Optional[str] = None,
    ) -> ArtistConnection:
        first_int: int = int(first or 20)
        items, has_next_page, total_count = await services.artist.get_connection(
            first=first_int,
            after=after,
            is_tracked=is_tracked,
            sort_by=sort_by,
            sort_direction=sort_direction,
            search=search,
        )

        edges = items

        page_info = PageInfo(
            has_next_page=has_next_page,
            has_previous_page=after is not None,
            start_cursor=services.artist.create_cursor(edges[0]) if edges else None,
            end_cursor=services.artist.create_cursor(edges[-1]) if edges else None,
        )

        return ArtistConnection(
            edges=edges, page_info=page_info, total_count=total_count
        )

    @strawberry.field
    async def artist(self, id: str) -> Optional[Artist]:
        return await services.artist.get_by_id(id)

    @strawberry.field
    async def albums(
        self,
        first: Optional[int] = 20,
        after: Optional[str] = None,
        artist_id: Optional[int] = None,
        downloaded: Optional[bool] = None,
        wanted: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_direction: Optional[str] = None,
        search: Optional[str] = None,
    ) -> AlbumConnection:
        first_int: int = int(first or 20)
        items, has_next_page, total_count = await services.album.get_connection(
            first=first_int,
            after=after,
            artist_id=artist_id,
            downloaded=downloaded,
            wanted=wanted,
            sort_by=sort_by,
            sort_direction=sort_direction,
            search=search,
        )

        edges = items

        page_info = PageInfo(
            has_next_page=has_next_page,
            has_previous_page=after is not None,
            start_cursor=services.album.create_cursor(edges[0]) if edges else None,
            end_cursor=services.album.create_cursor(edges[-1]) if edges else None,
        )

        return AlbumConnection(
            edges=edges, page_info=page_info, total_count=total_count
        )

    @strawberry.field
    async def album(self, id: str) -> Optional[Album]:
        return await services.album.get_by_id(id)

    @strawberry.field
    async def songs(
        self,
        first: Optional[int] = 20,
        after: Optional[str] = None,
        artist_id: Optional[int] = None,
        downloaded: Optional[bool] = None,
        unavailable: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_direction: Optional[str] = None,
        search: Optional[str] = None,
    ) -> SongConnection:
        first_int: int = int(first or 20)
        items, has_next_page, total_count = await services.song.get_connection(
            first=first_int,
            after=after,
            artist_id=artist_id,
            downloaded=downloaded,
            unavailable=unavailable,
            sort_by=sort_by,
            sort_direction=sort_direction,
            search=search,
        )

        edges = items

        page_info = PageInfo(
            has_next_page=has_next_page,
            has_previous_page=after is not None,
            start_cursor=services.song.create_cursor(edges[0]) if edges else None,
            end_cursor=services.song.create_cursor(edges[-1]) if edges else None,
        )

        return SongConnection(edges=edges, page_info=page_info, total_count=total_count)

    @strawberry.field
    async def song(self, id: str) -> Optional[Song]:
        return await services.song.get_by_id(id)

    @strawberry.field
    async def playlists(
        self,
        first: Optional[int] = 20,
        after: Optional[str] = None,
        enabled: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_direction: Optional[str] = None,
        search: Optional[str] = None,
    ) -> PlaylistConnection:
        first_int: int = int(first or 20)
        items, has_next_page, total_count = await services.playlist.get_connection(
            first=first_int,
            after=after,
            enabled=enabled,
            sort_by=sort_by,
            sort_direction=sort_direction,
            search=search,
        )

        edges = items

        page_info = PageInfo(
            has_next_page=has_next_page,
            has_previous_page=after is not None,
            start_cursor=None,
            end_cursor=None,
        )

        return PlaylistConnection(
            edges=edges, page_info=page_info, total_count=total_count
        )

    @strawberry.field
    async def playlist(self, id: str) -> Optional[Playlist]:
        return await services.playlist.get_by_id(id)

    @strawberry.field
    async def download_history(
        self,
        first: Optional[int] = 20,
        after: Optional[str] = None,
        entity_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> HistoryConnection:
        first_int: int = int(first or 20)
        items, has_next_page, total_count = await services.history.get_connection(
            first=first_int, after=after, entity_type=entity_type, status=status
        )

        edges: list[HistoryEdge] = [
            HistoryEdge(node=item, cursor=services.history.create_cursor(item))
            for item in items
        ]

        page_info = PageInfo(
            has_next_page=has_next_page,
            has_previous_page=after is not None,
            start_cursor=edges[0].cursor if edges else None,
            end_cursor=edges[-1].cursor if edges else None,
        )

        return HistoryConnection(
            edges=edges, page_info=page_info, total_count=total_count
        )

    @strawberry.field
    async def task_history(
        self,
        first: Optional[int] = 20,
        after: Optional[str] = None,
        status: Optional[str] = None,
        type: Optional[str] = None,
        entity_type: Optional[str] = None,
        search: Optional[str] = None,
    ) -> TaskHistoryConnection:
        first_int: int = int(first or 20)
        items, has_next_page, total_count = await services.task_history.get_connection(
            first=first_int,
            after=after,
            status=status,
            type=type,
            entity_type=entity_type,
            search=search,
        )

        edges = [
            TaskHistoryEdge(node=item, cursor=services.task_history.create_cursor(item))
            for item in items
        ]

        page_info = PageInfo(
            has_next_page=has_next_page,
            has_previous_page=after is not None,
            start_cursor=edges[0].cursor if edges else None,
            end_cursor=edges[-1].cursor if edges else None,
        )

        return TaskHistoryConnection(
            edges=edges, page_info=page_info, total_count=total_count
        )

    @strawberry.field
    async def queue_status(self) -> QueueStatus:
        """Get the current status of the Celery task queue."""
        status = await services.task_management.get_queue_status()

        # Convert the task_counts dict to a list of TaskCount objects
        # Filter out any null or empty task names as an additional safety measure
        task_counts = [
            TaskCount(task_name=name, count=count)
            for name, count in status["task_counts"].items()
            if name  # Skip null or empty names
        ]

        return QueueStatus(
            total_pending_tasks=status["total_pending_tasks"],
            task_counts=task_counts,
            queue_size=status["queue_size"],
        )

    @strawberry.field
    async def periodic_tasks(
        self, enabled_only: Optional[bool] = False
    ) -> List[PeriodicTask]:
        """Get all scheduled periodic tasks from Celery Beat."""
        if enabled_only:
            return await services.periodic_task.get_enabled()
        return await services.periodic_task.get_all()

    @strawberry.field
    async def system_health(self) -> SystemHealth:
        """Get overall system health including authentication status."""
        from asgiref.sync import sync_to_async

        from ..services.system_health import SystemHealthService

        # Use thread_sensitive=True to ensure Django ORM access works correctly
        auth_status = await sync_to_async(
            SystemHealthService.check_authentication_status, thread_sensitive=True
        )()
        can_download, reason = await sync_to_async(
            SystemHealthService.is_download_capable
        )()

        return SystemHealth(
            can_download=can_download,
            download_blocker_reason=reason,
            authentication=AuthenticationStatus(
                cookies_valid=auth_status.cookies_valid,
                cookies_error_type=auth_status.cookies_error_type,
                cookies_error_message=auth_status.cookies_error_message,
                cookies_expire_in_days=auth_status.cookies_expire_in_days,
                po_token_configured=auth_status.po_token_configured,
                po_token_valid=auth_status.po_token_valid,
                po_token_error_message=auth_status.po_token_error_message,
                spotify_user_auth_enabled=auth_status.spotify_user_auth_enabled,
                spotify_auth_mode=auth_status.spotify_auth_mode,
                spotify_token_valid=auth_status.spotify_token_valid,
                spotify_token_expired=auth_status.spotify_token_expired,
                spotify_token_expires_in_hours=auth_status.spotify_token_expires_in_hours,
                spotify_token_error_message=auth_status.spotify_token_error_message,
            ),
        )

    @strawberry.field
    async def spotify_search(
        self,
        query: str,
        types: Optional[List[str]] = None,
        limit: Optional[int] = 10,
    ) -> SpotifySearchResults:
        """
        Search Spotify's catalog for artists, albums, tracks, and playlists.

        This searches the Spotify API directly, not the local database.
        Results include an 'in_library' flag to indicate if items already exist locally.

        Args:
            query: Search query string
            types: List of types to search ('artist', 'album', 'track', 'playlist').
                   Defaults to all types.
            limit: Max results per type (default 10, max 50)
        """
        results = await services.spotify_search.search(
            query=query,
            types=types,
            limit=limit or 10,
        )

        # Convert service dataclasses to GraphQL types
        return SpotifySearchResults(
            artists=[
                SpotifySearchArtist(
                    id=a.id,
                    name=a.name,
                    spotify_uri=a.spotify_uri,
                    image_url=a.image_url,
                    follower_count=a.follower_count,
                    genres=a.genres,
                    in_library=a.in_library,
                    local_id=a.local_id,
                )
                for a in results.artists
            ],
            albums=[
                SpotifySearchAlbum(
                    id=a.id,
                    name=a.name,
                    spotify_uri=a.spotify_uri,
                    image_url=a.image_url,
                    artist_name=a.artist_name,
                    artist_id=a.artist_id,
                    release_date=a.release_date,
                    album_type=a.album_type,
                    total_tracks=a.total_tracks,
                    in_library=a.in_library,
                    local_id=a.local_id,
                )
                for a in results.albums
            ],
            tracks=[
                SpotifySearchTrack(
                    id=t.id,
                    name=t.name,
                    spotify_uri=t.spotify_uri,
                    artist_name=t.artist_name,
                    artist_id=t.artist_id,
                    album_name=t.album_name,
                    album_id=t.album_id,
                    duration_ms=t.duration_ms,
                    in_library=t.in_library,
                    local_id=t.local_id,
                )
                for t in results.tracks
            ],
            playlists=[
                SpotifySearchPlaylist(
                    id=p.id,
                    name=p.name,
                    spotify_uri=p.spotify_uri,
                    image_url=p.image_url,
                    owner_name=p.owner_name,
                    track_count=p.track_count,
                    description=p.description,
                    in_library=p.in_library,
                    local_id=p.local_id,
                )
                for p in results.playlists
            ],
        )
