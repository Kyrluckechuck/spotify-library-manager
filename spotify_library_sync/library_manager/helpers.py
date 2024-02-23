from .models import Album, Artist
from spotify_aac_downloader.spotify_aac_downloader import Config, main as downloader_main

from huey import crontab
from huey.contrib.djhuey import task, HUEY as rawHuey
from huey.api import Task
from huey_monitor.tqdm import ProcessInfo

from django.db.models.functions import Now

@task()
def fetch_all_albums_for_artist(artist_id: int):
    artist = Artist.objects.get(id=artist_id)
    downloader_config = Config()
    downloader_config.artist_to_fetch = artist.gid
    downloader_config.urls = []
    downloader_main(downloader_config)

@task(context=True)
def download_missing_albums_for_artist(artist_id: int, task: Task = None):
    artist = Artist.objects.get(id=artist_id)
    missing_albums = Album.objects.filter(artist=artist, downloaded=False, wanted=True)
    print(f"missing albums search for artist {artist.id} found {missing_albums.count()}")
    downloader_config = Config()
    if task is not None:
        process_info = ProcessInfo(task, desc=f"artist missing album download (artist.id: {artist.id})", total=1000)
        downloader_config.process_info = process_info
    # TODO: Figure out why the Config instance is persisting between runs, somehow 😕
    downloader_config.urls = []
    for missing_album in missing_albums:
        downloader_config.urls.append(missing_album.spotify_uri)

    print(f"missing albums search for artist {artist.id} kicking off {len(downloader_config.urls)}")
    downloader_main(downloader_config)
    artist.last_synced_at = Now()
    artist.save()

@task(context=True)
def download_playlist(playlist_url: str, tracked: bool = True, task: Task = None):
    downloader_config = Config()
    downloader_config.urls = [playlist_url]
    downloader_config.track_artists = tracked
    if task is not None:
        process_info = ProcessInfo(task, desc='playlist download', total=1000)
        downloader_config.process_info = process_info
    downloader_main(downloader_config)

# Disable period tasks for now
# @huey.periodic_task(crontab(minute='0', hour='*/3'))
@task(priority=10)
def update_tracked_artists():
    # Check setting, if enabled, auto update
    all_tracked_artists = Artist.objects.filter(tracked=True).all()
    pending_tasks: list[Task] = rawHuey.pending()

    pending_artist_fetches: list[int] = []

    for pending_task in pending_tasks:
        if pending_task.name == 'fetch_all_albums_for_artist':
            pending_artist_fetches.append(pending_task.args[0])

    for artist in all_tracked_artists:
        if artist.id in pending_artist_fetches:
            continue

        fetch_all_albums_for_artist(artist.id)

# @huey.periodic_task(crontab(minute='0', hour='*/3'))
# @task(priority=10)
def download_missing_tracked_artists():
    # Check setting, if enabled, auto download
    all_tracked_artists = Artist.objects.filter(tracked=True).all()
    pending_tasks: list[Task] = rawHuey.pending()

    pending_artist_downloads: list[int] = []

    for pending_task in pending_tasks:
        if pending_task.name == 'download_missing_albums_for_artist':
            pending_artist_downloads.append(pending_task.args[0])

    for artist in all_tracked_artists:
        if artist.id in pending_artist_downloads:
            continue

        download_missing_albums_for_artist(artist.id)
