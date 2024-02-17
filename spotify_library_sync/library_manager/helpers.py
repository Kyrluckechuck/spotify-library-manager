from .models import Album, Artist
from spotify_aac_downloader.spotify_aac_downloader import Config, main as downloader_main
from huey.contrib.djhuey import task

@task()
def fetch_all_albums_for_artist(artist_id: int):
    artist = Artist.objects.get(id=artist_id)
    downloader_config = Config()
    downloader_config.artist_to_fetch = artist.gid
    downloader_main(downloader_config)

@task()
def download_missing_albums_for_artist(artist_id: int):
    artist = Artist.objects.get(id=artist_id)
    missing_albums = Album.objects.filter(artist=artist, downloaded=False, wanted=True)
    downloader_config = Config()
    for missing_album in missing_albums:
        downloader_config.urls.append(missing_album.spotify_uri)
    downloader_main(downloader_config)

@task()
def download_playlist(playlist_url: str, tracked: bool = True):
    downloader_config = Config()
    downloader_config.urls = [playlist_url]
    downloader_config.track_artists = tracked
    downloader_main(downloader_config)
