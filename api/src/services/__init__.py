from typing import Optional
from functools import cached_property

from .artist import ArtistService
from .album import AlbumService
from .playlist import PlaylistService
from .history import DownloadHistoryService

class ServiceRegistry:
    _instance: Optional['ServiceRegistry'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @cached_property
    def artist(self) -> ArtistService:
        return ArtistService()

    @cached_property
    def album(self) -> AlbumService:
        return AlbumService()

    @cached_property
    def playlist(self) -> PlaylistService:
        return PlaylistService()

    @cached_property
    def history(self) -> DownloadHistoryService:
        return DownloadHistoryService()

services = ServiceRegistry() 