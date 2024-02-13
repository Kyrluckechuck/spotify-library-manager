from .models import Artist
from spotify_aac_downloader.spotify_aac_downloader import Config, main as downloader_main

def download_all_for_artist(artist: Artist):
    downloader_config = Config()
    downloader_config.artist_to_download = artist.gid
    downloader_main(downloader_config)
