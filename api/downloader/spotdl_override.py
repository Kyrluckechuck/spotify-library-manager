import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional, Tuple, Union

from spotdl.download.downloader import Downloader
from spotdl.types.options import DownloaderOptionalOptions, DownloaderOptions
from spotdl.types.song import Song
from spotdl.utils.spotify import SpotifyClient


# Class SpotDl
# Monkeypatch The Spotdl class to only init SpotifyClient if it doesn't already exist
def __init__(
    self: "Downloader",
    client_id: str,
    client_secret: str,
    user_auth: bool = False,
    cache_path: Optional[str] = None,
    no_cache: bool = False,
    headless: bool = False,
    downloader_settings: Optional[
        Union[DownloaderOptionalOptions, DownloaderOptions]
    ] = None,
    loop: Optional[asyncio.AbstractEventLoop] = None,
    auth_token: Optional[str] = None,
) -> None:
    """
    Initialize the Spotdl class

    ### Arguments
    - client_id: Spotify client id
    - client_secret: Spotify client secret
    - user_auth: If true, user will be prompted to authenticate
    - cache_path: Path to cache directory
    - no_cache: If true, no cache will be used
    - headless: If true, no browser will be opened
    - downloader_settings: Settings for the downloader
    - loop: Event loop to use
    - auth_token: OAuth access token (bypasses client credentials if provided)
    """

    if downloader_settings is None:
        downloader_settings = {}

    # Initialize spotify client
    if SpotifyClient._instance is None:
        # If OAuth token is provided, use it directly; otherwise use client credentials
        if auth_token:
            # For OAuth authentication, pass the token directly
            # This bypasses client credentials and uses the OAuth token
            SpotifyClient.init(
                client_id=client_id or "",
                client_secret=client_secret or "",
                user_auth=user_auth,
                cache_path=cache_path,
                no_cache=no_cache,
                headless=headless,
                auth_token=auth_token,
            )
        else:
            # Standard client credentials authentication
            SpotifyClient.init(
                client_id=client_id,
                client_secret=client_secret,
                user_auth=user_auth,
                cache_path=cache_path,
                no_cache=no_cache,
                headless=headless,
            )

    # Initialize downloader
    self.downloader = Downloader(
        settings=downloader_settings,
        loop=loop,
    )


# Class Spotdl.download.downloader.Downloader
# Monkeypatch to handle asyncio event loops not correctly assigning
def download_song(self: "Downloader", song: Song) -> Tuple[Song, Optional[Path]]:
    """
    Download a single song.

    ### Arguments
    - song: The song to download.

    ### Returns
    - tuple with the song and the path to the downloaded file if successful.
    """
    # Check if there's already a running event loop
    try:
        asyncio.get_running_loop()
        # There's a running loop - we need to run download in a separate thread
        # to avoid "this event loop is already running" error
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_download_song_sync, self, song)
            result = future.result()
            return result
    except RuntimeError:
        # No running loop - proceed normally
        pass

    # Ensure we have a valid event loop in this thread
    try:
        current_loop = asyncio.get_event_loop()
        if current_loop.is_closed():
            raise RuntimeError("Current event loop is closed")
        # Check if the loop belongs to this thread
        if current_loop != self.loop:
            asyncio.set_event_loop(self.loop)
    except RuntimeError:
        # No event loop exists in this thread, set our loop
        asyncio.set_event_loop(self.loop)

    self.progress_handler.set_song_count(1)

    results = self.download_multiple_songs([song])

    # Type cast to match expected return type
    result = results[0]
    return result  # type: ignore


def _download_song_sync(
    downloader: "Downloader", song: Song
) -> Tuple[Song, Optional[Path]]:
    """
    Helper function to download a song synchronously in a separate thread.
    This avoids event loop conflicts when called from an async context.
    """
    # In this new thread, there's no event loop yet
    asyncio.set_event_loop(downloader.loop)
    downloader.progress_handler.set_song_count(1)
    results = downloader.download_multiple_songs([song])
    return results[0]  # type: ignore
