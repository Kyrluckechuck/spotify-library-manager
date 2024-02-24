from .models import Album, Artist, TrackedPlaylist
from . import helpers
from spotify_aac_downloader.spotify_aac_downloader import Config, main as downloader_main

from huey import crontab
import huey.contrib.djhuey as huey
from huey.api import Task
from huey_monitor.tqdm import ProcessInfo

from django.db.models.functions import Now

@huey.task()
def fetch_all_albums_for_artist(artist_id: int):
    artist = Artist.objects.get(id=artist_id)
    downloader_config = Config()
    downloader_config.artist_to_fetch = artist.gid
    downloader_config.urls = []
    downloader_main(downloader_config)

@huey.task(context=True)
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

@huey.task(context=True)
def download_playlist(playlist_url: str, tracked: bool = True, task: Task = None):
    downloader_config = Config()
    downloader_config.urls = [playlist_url]
    downloader_config.track_artists = tracked
    if task is not None:
        process_info = ProcessInfo(task, desc='playlist download', total=1000)
        downloader_config.process_info = process_info
    downloader_main(downloader_config)

# Disable period tasks for now
@huey.periodic_task(crontab(minute='0', hour='*/2'))
# @huey.task(priority=10)
def update_tracked_artists():
    all_tracked_artists = Artist.objects.filter(tracked=True).order_by("last_synced_at", "added_at", "id")
    existing_tasks = helpers.get_all_tasks_with_name('fetch_all_albums_for_artist')
    already_enqueued_artists = helpers.convert_first_task_args_to_list(existing_tasks)
    helpers.update_tracked_artists_albums(already_enqueued_artists, all_tracked_artists)

@huey.periodic_task(crontab(minute='15', hour='*/4'))
# @huey.task(priority=10)
def download_missing_tracked_artists():
    all_tracked_artists = Artist.objects.filter(tracked=True).order_by("last_synced_at", "added_at", "id")
    existing_tasks = helpers.get_all_tasks_with_name('download_missing_albums_for_artist')
    already_enqueued_artists = helpers.convert_first_task_args_to_list(existing_tasks)
    helpers.download_missing_tracked_artists(already_enqueued_artists, all_tracked_artists)

@huey.periodic_task(crontab(minute='0', hour='*/6'))
# @huey.task(priority=10)
def sync_tracked_playlists():
    all_enabled_playlists = TrackedPlaylist.objects.filter(enabled=True).order_by("last_synced_at", "id")
    existing_tasks = helpers.get_all_tasks_with_name('download_playlist')
    already_enqueued_playlists = helpers.convert_first_task_args_to_list(existing_tasks)
    helpers.download_non_enqueued_playlists(already_enqueued_playlists, all_enabled_playlists)