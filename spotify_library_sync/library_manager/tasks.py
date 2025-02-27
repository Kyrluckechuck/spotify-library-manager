import time

from django.conf import settings

from .models import Album, Artist, DownloadHistory, Song, TrackedPlaylist, ALBUM_TYPES_TO_DOWNLOAD, EXTRA_GROUPS_TO_IGNORE
from . import helpers
from downloader.utils import sanitize_and_strip_url
from downloader.spotdl_wrapper import SpotdlWrapper
from downloader.spotipy_tasks import track_artists_in_playlist
from lib.config_class import Config

from huey import crontab
import huey.contrib.djhuey as huey
from huey.api import Task
from huey_monitor.tqdm import ProcessInfo

from django.db.models.functions import Now
from django.utils import timezone

spotdl_wrapper = SpotdlWrapper(Config())

@huey.task(context=True, priority=3)
def fetch_all_albums_for_artist(artist_id: int, task: Task = None):
    artist = Artist.objects.get(id=artist_id)
    downloader_config = Config()
    downloader_config.artist_to_fetch = artist.gid
    downloader_config.urls = []
    if task is not None:
        process_info = ProcessInfo(task, desc=f"fetch all albums for artist (artist.id: {artist.id})")
        downloader_config.process_info = process_info
    spotdl_wrapper.execute(downloader_config)

@huey.task(context=True, priority=1)
def download_missing_albums_for_artist(artist_id: int, task: Task = None, delay: int = 0):
    # Add delay (if applicable) to reduce chance of flagging when backfilling library
    time.sleep(delay)

    artist = Artist.objects.get(id=artist_id)
    missing_albums = Album.objects.filter(artist=artist, downloaded=False, wanted=True, album_type__in=ALBUM_TYPES_TO_DOWNLOAD).exclude(album_group__in=EXTRA_GROUPS_TO_IGNORE)
    print(f"missing albums search for artist {artist.id} found {missing_albums.count()}")
    downloader_config = Config()
    if task is not None:
        process_info = ProcessInfo(task, desc=f"artist missing album download (artist.id: {artist.id})", total=1000)
        downloader_config.process_info = process_info
    downloader_config.urls = []  # This must be reset or it will persist between runs
    if missing_albums.count() > 0:
        for missing_album in missing_albums:
            downloader_config.urls.append(missing_album.spotify_uri)

        print(f"missing albums search for artist {artist.id} kicking off {len(downloader_config.urls)}")
        spotdl_wrapper.execute(downloader_config)
    else:
        print(f"missing albums search for artist {artist.id} is skipping since there are none missing")
    artist.last_synced_at = Now()
    artist.save()

@huey.task(context=True, priority=2)
def sync_tracked_playlist(tracked_playlist: TrackedPlaylist, task: Task = None):
    helpers.enqueue_playlists([tracked_playlist], priority=task.priority)

@huey.task(context=True, priority=2)
def download_playlist(playlist_url: str, tracked: bool = True, task: Task = None):
    playlist_url = sanitize_and_strip_url(playlist_url)

    downloader_config = Config(
        urls=[playlist_url],
        track_artists = tracked
    )

    if task is not None:
        process_info = ProcessInfo(task, desc='playlist download', total=1000)
        downloader_config.process_info = process_info
    spotdl_wrapper.execute(downloader_config)

@huey.task(context=True, priority=0)
def retry_all_missing_known_songs(task: Task = None):
    missing_known_songs_list = Song.objects.filter(bitrate=0,unavailable=False).order_by("created_at").select_related('primary_artist').filter(primary_artist__tracked=True)[:100]
    failed_known_songs_list = Song.objects.filter(failed_count__gt=0,bitrate=0,unavailable=False).order_by("created_at")[:100]
    # Combine results for iterating
    missing_known_songs_list = missing_known_songs_list | failed_known_songs_list

    if missing_known_songs_list.count() == 0:
        print("All songs downloaded, exiting missing known song loop!")
        return

    failed_song_array = [song.spotify_uri for song in missing_known_songs_list]

    print(f"Downloading {len(failed_song_array)} missing songs")
    downloader_config = Config(
        urls=failed_song_array,
        track_artists = False
    )

    if task is not None:
        process_info = ProcessInfo(task, desc='missing/failed song download', total=1000)
        downloader_config.process_info = process_info
    spotdl_wrapper.execute(downloader_config)

    # Queue up next batch
    retry_all_missing_known_songs()



@huey.task(context=True, priority=3)
def download_extra_album_types_for_artist(artist_id: int, task: Task = None):
    artist = Artist.objects.get(id=artist_id)
    missing_albums = Album.objects.filter(artist=artist, downloaded=False, wanted=True, album_group__in=EXTRA_GROUPS_TO_IGNORE)
    print(f"extra album missing albums search for artist {artist.id} found {missing_albums.count()}")
    downloader_config = Config()
    if task is not None:
        process_info = ProcessInfo(task, desc=f"extra album artist missing album download (artist.id: {artist.id})", total=1000)
        downloader_config.process_info = process_info
    downloader_config.urls = []  # This must be reset or it will persist between runs
    if missing_albums.count() > 0:
        for missing_album in missing_albums:
            downloader_config.urls.append(missing_album.spotify_uri)

        print(f"extra album missing albums search for artist {artist.id} kicking off {len(downloader_config.urls)}")
        spotdl_wrapper.execute(downloader_config)
    else:
        print(f"extra album missing albums search for artist {artist.id} is skipping since there are none missing")
    artist.last_synced_at = Now()
    artist.save()

@huey.task(context=True, priority=3)
def sync_tracked_playlist_artists(playlist: TrackedPlaylist, task: Task = None):
    # Given a playlist, track the artists without actually downloading the playlist (potentially, again)
    track_artists_in_playlist(playlist.url, task)

@huey.periodic_task(crontab(minute='0', hour='*/8'), priority=1, context=True)
def update_tracked_artists(task: Task = None):
    all_tracked_artists = Artist.objects.filter(tracked=True).order_by("last_synced_at", "added_at", "id")
    existing_tasks = helpers.get_all_tasks_with_name('fetch_all_albums_for_artist')
    already_enqueued_artists = helpers.convert_first_task_args_to_list(existing_tasks)
    helpers.update_tracked_artists_albums(already_enqueued_artists, all_tracked_artists, priority=task.priority)

# Severely throttling automatic playlist download for tracked artists for the time being;
# There is a high likelyhood of being flagged due to high usage at the moment and a new scalable solution needs to be investigated.
@huey.periodic_task(crontab(minute='45', hour='*/8'), priority=0, context=True)
def download_missing_tracked_artists(task: Task = None):
    if settings.disable_missing_tracked_artist_download:
        print(f"Skipping queued missing tracked artists due to disable_missing_tracked_artist_download setting")
        return
    
    twelve_hours_ago = timezone.now() - timezone.timedelta(hours=12)
    recently_downloaded_songs = DownloadHistory.objects.filter(added_at__gte=twelve_hours_ago)
    if (recently_downloaded_songs.count() > 250):
        print(f"Skipping queued missing tracked artists due to quantity of recent downloads ({recently_downloaded_songs.count()})")
        return
    # Limit to only desired album types (ignoring `appears_on`), and limit results so this won't throttle
    all_tracked_artists = Artist.objects.filter(tracked=True, album__downloaded=False, album__wanted=True, album__album_type__in=ALBUM_TYPES_TO_DOWNLOAD).exclude(album__album_group__in=EXTRA_GROUPS_TO_IGNORE).distinct().order_by("last_synced_at", "added_at", "id")[:150]
    existing_tasks = helpers.get_all_tasks_with_name('download_missing_albums_for_artist')
    already_enqueued_artists = helpers.convert_first_task_args_to_list(existing_tasks)
    helpers.download_missing_tracked_artists(already_enqueued_artists, all_tracked_artists, priority=task.priority)

@huey.periodic_task(crontab(minute='0', hour='*/4'), priority=1, context=True)
def sync_tracked_playlists(task: Task = None):
    all_enabled_playlists = TrackedPlaylist.objects.filter(enabled=True).order_by("last_synced_at", "id")
    helpers.enqueue_playlists(all_enabled_playlists, priority=task.priority)

@huey.periodic_task(crontab(minute='0', hour='6'), priority=10)
def cleanup_huey_history():
    helpers.cleanup_huey_history()
