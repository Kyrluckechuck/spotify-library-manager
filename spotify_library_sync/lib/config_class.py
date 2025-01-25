from pathlib import Path

from django.conf import settings
from huey_monitor.tqdm import ProcessInfo

class Config:
    def __init__(
        self,
        urls: list[str] = [],
        cookies_location: Path = Path(settings.cookies_location),
        po_token: str = settings.po_token,
        log_level: str = settings.log_level,
        no_lrc: bool = settings.no_lrc,
        overwrite: bool = settings.overwrite,
        track_artists: bool = False,
        artist_to_fetch: str = None,
        print_exceptions: bool = True,
        process_info: ProcessInfo = None,

    ):
        self.urls = urls
        self.cookies_location = cookies_location
        self.po_token = po_token
        self.log_level = log_level
        self.no_lrc = no_lrc
        self.overwrite = overwrite
        self.track_artists = track_artists
        self.artist_to_fetch = artist_to_fetch
        self.print_exceptions = print_exceptions
        self.process_info = process_info
