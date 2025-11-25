from functools import cached_property
from typing import Optional

from .album import AlbumService
from .artist import ArtistService
from .downloader import DownloaderService
from .history import DownloadHistoryService
from .periodic_task import PeriodicTaskService
from .playlist import PlaylistService
from .song import SongService
from .spotify_search import SpotifySearchService
from .task_history import TaskHistoryService
from .task_management import TaskManagementService


class ServiceRegistry:
    _instance: Optional["ServiceRegistry"] = None

    def __new__(cls) -> "ServiceRegistry":
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

    @cached_property
    def task_history(self) -> TaskHistoryService:
        return TaskHistoryService()

    @cached_property
    def downloader(self) -> DownloaderService:
        return DownloaderService()

    @cached_property
    def song(self) -> SongService:
        return SongService()

    @cached_property
    def task_management(self) -> TaskManagementService:
        return TaskManagementService()

    @cached_property
    def periodic_task(self) -> PeriodicTaskService:
        return PeriodicTaskService()

    @cached_property
    def spotify_search(self) -> SpotifySearchService:
        return SpotifySearchService()


services = ServiceRegistry()
