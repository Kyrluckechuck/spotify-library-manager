from .models import Artist, TrackedPlaylist
from . import tasks

from huey.contrib.djhuey import HUEY as rawHuey
from huey.api import Task

from django.db import connection

def get_all_tasks_with_name(task_name: str):
    potential_tasks: list[Task] = rawHuey.pending()

    found_tasks: list[int] = []

    for potential_task in potential_tasks:
        if potential_task.name == task_name:
            found_tasks.append(potential_task)

    return found_tasks

def convert_first_task_args_to_list(pending_tasks: list[Task]) -> list[int] | list[str]:
    pending_args: list[int] | list[str] = []

    for pending_task in pending_tasks:
        pending_args.append(pending_task.args[0])

    return pending_args

def update_tracked_artists_albums(already_enqueued_artists: list[int], artists_to_enqueue: list[Artist], priority: int | None = None):
    for artist in artists_to_enqueue:
        if artist.id in already_enqueued_artists:
            continue

        extra_args = {}
        if priority is not None:
            extra_args['priority'] = priority
        tasks.fetch_all_albums_for_artist(artist.id, **extra_args)

def download_missing_tracked_artists(already_enqueued_artists: list[int], artists_to_enqueue: list[Artist], priority: int | None = None):
    for artist in artists_to_enqueue:
        if artist.id in already_enqueued_artists:
            continue

        extra_args = {}
        if priority is not None:
            extra_args['priority'] = priority
        tasks.download_missing_albums_for_artist(artist.id, **extra_args)


def download_non_enqueued_playlists(already_enqueued_playlists: list[str], playlists_to_enqueue: list[TrackedPlaylist], priority: int | None = None):
    for playlist in playlists_to_enqueue:
        if playlist.url in already_enqueued_playlists:
            continue

        extra_args = {}
        if priority is not None:
            extra_args['priority'] = priority
        tasks.download_playlist(playlist_url=playlist.url, tracked=playlist.auto_track_artists, **extra_args)

def enqueue_playlists(playlists_to_enqueue: list[TrackedPlaylist], priority=None):
    existing_tasks = get_all_tasks_with_name('download_playlist')
    already_enqueued_playlists = convert_first_task_args_to_list(existing_tasks)
    download_non_enqueued_playlists(already_enqueued_playlists, playlists_to_enqueue, priority=priority)

def cleanup_huey_history():
    with connection.cursor() as cursor:
        cursor.execute("UPDATE huey_monitor_taskmodel SET parent_task_id = NULL, state_id = NULL WHERE create_dt < DATETIME('now', '-3 day');")
        cursor.execute("DELETE FROM huey_monitor_signalinfomodel WHERE create_dt < DATETIME('now', '-3 day');")
        cursor.execute("DELETE FROM huey_monitor_taskmodel WHERE create_dt < DATETIME('now', '-3 day');")
        cursor.execute("VACUUM;")
