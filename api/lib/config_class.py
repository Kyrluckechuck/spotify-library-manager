from pathlib import Path
from typing import List, Optional

from django.conf import settings

from huey_monitor.tqdm import ProcessInfo


class Config:
    def __init__(
        self,
        urls: Optional[List[str]] = None,
        cookies_location: Optional[Path] = None,
        po_token: Optional[str] = None,
        log_level: Optional[str] = None,
        no_lrc: Optional[bool] = None,
        overwrite: Optional[bool] = None,
        track_artists: bool = False,
        artist_to_fetch: Optional[str] = None,
        print_exceptions: bool = True,
        process_info: Optional[ProcessInfo] = None,
        force_playlist_resync: bool = False,
    ):
        # Handle settings with defaults
        self.cookies_location = cookies_location or Path(
            getattr(settings, "cookies_location", "/config/cookies.txt")
        )
        self.po_token = (
            po_token if po_token is not None else getattr(settings, "po_token", None)
        )
        self.log_level = (
            log_level
            if log_level is not None
            else getattr(settings, "log_level", "INFO")
        )
        self.no_lrc = (
            no_lrc if no_lrc is not None else getattr(settings, "no_lrc", False)
        )
        self.overwrite = (
            overwrite
            if overwrite is not None
            else getattr(settings, "overwrite", False)
        )

        # Direct assignments
        self.urls = urls or []
        self.track_artists = track_artists
        self.artist_to_fetch = artist_to_fetch
        self.print_exceptions = print_exceptions
        self.process_info = process_info
        self.force_playlist_resync = force_playlist_resync
