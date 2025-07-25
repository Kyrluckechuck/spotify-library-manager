import asyncio
from pathlib import Path
from typing import Optional, Union, Tuple

from spotdl._version import __version__
from spotdl.download.downloader import Downloader
from spotdl.types.options import DownloaderOptionalOptions, DownloaderOptions
from spotdl.types.song import Song
from spotdl.utils.spotify import SpotifyClient

# Class SpotDl
# Monkeypatch The Spotdl class to only init SpotifyClient if it doesn't already exist
def __init__(
    self,
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
):
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
    """

    if downloader_settings is None:
        downloader_settings = {}

    # Initialize spotify client
    if (SpotifyClient._instance is None):
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
def download_song(self, song: Song) -> Tuple[Song, Optional[Path]]:
    """
    Download a single song.

    ### Arguments
    - song: The song to download.

    ### Returns
    - tuple with the song and the path to the downloaded file if successful.
    """
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(self.loop)

    self.progress_handler.set_song_count(1)

    results = self.download_multiple_songs([song])

    return results[0]
