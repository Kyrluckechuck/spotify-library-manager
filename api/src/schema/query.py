from typing import List, Optional
import strawberry
from ..types.models import (
    Artist, Album, Playlist, DownloadHistory,
    ArtistConnection, AlbumConnection, PlaylistConnection, HistoryConnection,
    PageInfo
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
        search: Optional[str] = None
    ) -> ArtistConnection:
        items, has_next_page, total_count = await services.artist.get_connection(
            first=first,
            after=after,
            is_tracked=is_tracked,
            search=search
        )
        
        edges = [
            strawberry.type("ArtistEdge")(
                node=item,
                cursor=services.artist.create_cursor(item)
            ) for item in items
        ]
        
        page_info = PageInfo(
            has_next_page=has_next_page,
            has_previous_page=after is not None,
            start_cursor=edges[0].cursor if edges else None,
            end_cursor=edges[-1].cursor if edges else None
        )
        
        return ArtistConnection(
            edges=edges,
            page_info=page_info,
            total_count=total_count
        )

    @strawberry.field
    async def artist(self, id: str) -> Optional[Artist]:
        return await services.artist.get_by_id(id)

    @strawberry.field
    async def albums(
        self,
        first: Optional[int] = 20,
        after: Optional[str] = None,
        artist_id: Optional[str] = None,
        is_downloaded: Optional[bool] = None,
        is_wanted: Optional[bool] = None,
        search: Optional[str] = None
    ) -> AlbumConnection:
        items, has_next_page, total_count = await services.album.get_connection(
            first=first,
            after=after,
            artist_id=artist_id,
            is_downloaded=is_downloaded,
            is_wanted=is_wanted,
            search=search
        )
        
        edges = [
            strawberry.type("AlbumEdge")(
                node=item,
                cursor=services.album.create_cursor(item)
            ) for item in items
        ]
        
        page_info = PageInfo(
            has_next_page=has_next_page,
            has_previous_page=after is not None,
            start_cursor=edges[0].cursor if edges else None,
            end_cursor=edges[-1].cursor if edges else None
        )
        
        return AlbumConnection(
            edges=edges,
            page_info=page_info,
            total_count=total_count
        )

    @strawberry.field
    async def album(self, id: str) -> Optional[Album]:
        return await services.album.get_by_id(id)

    @strawberry.field
    async def playlists(
        self,
        first: Optional[int] = 20,
        after: Optional[str] = None,
        is_tracked: Optional[bool] = None,
        search: Optional[str] = None
    ) -> PlaylistConnection:
        items, has_next_page, total_count = await services.playlist.get_connection(
            first=first,
            after=after,
            is_tracked=is_tracked,
            search=search
        )
        
        edges = [
            strawberry.type("PlaylistEdge")(
                node=item,
                cursor=services.playlist.create_cursor(item)
            ) for item in items
        ]
        
        page_info = PageInfo(
            has_next_page=has_next_page,
            has_previous_page=after is not None,
            start_cursor=edges[0].cursor if edges else None,
            end_cursor=edges[-1].cursor if edges else None
        )
        
        return PlaylistConnection(
            edges=edges,
            page_info=page_info,
            total_count=total_count
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
        status: Optional[str] = None
    ) -> HistoryConnection:
        items, has_next_page, total_count = await services.history.get_connection(
            first=first,
            after=after,
            entity_type=entity_type,
            status=status
        )
        
        edges = [
            strawberry.type("HistoryEdge")(
                node=item,
                cursor=services.history.create_cursor(item)
            ) for item in items
        ]
        
        page_info = PageInfo(
            has_next_page=has_next_page,
            has_previous_page=after is not None,
            start_cursor=edges[0].cursor if edges else None,
            end_cursor=edges[-1].cursor if edges else None
        )
        
        return HistoryConnection(
            edges=edges,
            page_info=page_info,
            total_count=total_count
        ) 