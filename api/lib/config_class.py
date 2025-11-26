from pathlib import Path
from typing import List, Optional

from django.conf import settings


class Config:
    def __init__(
        self,
        urls: Optional[List[str]] = None,
        cookies_location: Optional[Path] = None,
        youtube_cookies_location: Optional[Path] = None,
        spotify_user_auth_enabled: Optional[bool] = None,
        po_token: Optional[str] = None,
        log_level: Optional[str] = None,
        spotdl_log_level: Optional[str] = None,
        no_lrc: Optional[bool] = None,
        overwrite: Optional[bool] = None,
        track_artists: bool = False,
        artist_to_fetch: Optional[str] = None,
        print_exceptions: bool = True,
        force_playlist_resync: bool = False,
    ):
        # Handle YouTube cookies with backwards compatibility
        self.youtube_cookies_location = youtube_cookies_location or Path(
            getattr(
                settings,
                "youtube_cookies_location",
                "/config/youtube_music_cookies.txt",
            )
        )
        # Legacy fallback: cookies_location → youtube_cookies_location
        if cookies_location:
            self.youtube_cookies_location = Path(cookies_location)
        self.cookies_location = self.youtube_cookies_location  # Backwards compat

        # Handle Spotify user authentication for private playlists
        self.spotify_user_auth_enabled = (
            spotify_user_auth_enabled
            if spotify_user_auth_enabled is not None
            else getattr(settings, "spotify_user_auth_enabled", False)
        )
        self.po_token = (
            po_token if po_token is not None else getattr(settings, "po_token", None)
        )
        self.log_level = (
            log_level
            if log_level is not None
            else getattr(settings, "log_level", "INFO")
        )
        # Separate log level for spotdl library (defaults to INFO to avoid excessive verbosity)
        self.spotdl_log_level = (
            spotdl_log_level
            if spotdl_log_level is not None
            else getattr(settings, "spotdl_log_level", "INFO")
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
        self.force_playlist_resync = force_playlist_resync
