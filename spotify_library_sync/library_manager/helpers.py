from .models import Artist
from spotify_aac_downloader.spotify_aac_downloader import Config, main as downloader_main
from huey.contrib.djhuey import task

@task()
def download_all_for_artist(artist_id: int):
    artist = Artist.objects.get(id=artist_id)
    downloader_config = Config()
    downloader_config.artist_to_download = artist.gid
    downloader_main(downloader_config)

@task()
def download_playlist(playlist_url: str, tracked: bool = True):
    downloader_config = Config()
    downloader_config.urls = [playlist_url]
    downloader_config.track_artists = tracked
    downloader_main(downloader_config)
