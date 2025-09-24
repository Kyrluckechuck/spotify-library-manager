from typing import Optional

import strawberry

from ..graphql_types.models import (
    Album,
    AlbumConnection,
    Artist,
    ArtistConnection,
    HistoryConnection,
    HistoryEdge,
    PageInfo,
    Playlist,
    PlaylistConnection,
    QueueStatus,
    Song,
    SongConnection,
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
        search: Optional[str] = None,
    ) -> ArtistConnection:
        first_int: int = int(first or 20)
        items, has_next_page, total_count = await services.artist.get_connection(
            first=first_int, after=after, is_tracked=is_tracked, search=search
        )

        edges = items

        page_info = PageInfo(
            has_next_page=has_next_page,
            has_previous_page=after is not None,
            start_cursor=None,
            end_cursor=None,
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
            search=search,
        )

        edges = items

        page_info = PageInfo(
            has_next_page=has_next_page,
            has_previous_page=after is not None,
            start_cursor=None,
            end_cursor=None,
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
            search=search,
        )

        edges = items

        page_info = PageInfo(
            has_next_page=has_next_page,
            has_previous_page=after is not None,
            start_cursor=None,
            end_cursor=None,
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
            first=first_int, after=after, enabled=enabled, search=search
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
        """Get the current status of the Huey task queue."""
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
