from .models import Artist
from . import tasks

from huey.contrib.djhuey import HUEY as rawHuey
from huey.api import Task

def get_all_tasks_with_name(task_name: str):
    potential_tasks: list[Task] = rawHuey.pending()

    found_tasks: list[int] = []

    for potential_task in potential_tasks:
        if potential_task.name == task_name:
            found_tasks.append(potential_task)

    return found_tasks

def convert_first_task_args_to_list(pending_tasks: list[Task]):
    pending_args: list[int] = []

    for pending_task in pending_tasks:
        pending_args.append(pending_task.args[0])

    return pending_args

def update_tracked_artists_albums(already_enqueued_artists: list[int], artists_to_enqueue: list[Artist]):
    already_enqueued_artists: list[int] = []

    for artist in artists_to_enqueue:
        if artist.id in already_enqueued_artists:
            continue

        tasks.fetch_all_albums_for_artist(artist.id)

def download_missing_tracked_artists(already_enqueued_artists: list[int], artists_to_enqueue: list[Artist]):
    already_enqueued_artists: list[int] = []

    for artist in artists_to_enqueue:
        if artist.id in already_enqueued_artists:
            continue

        tasks.download_missing_albums_for_artist(artist.id)

# Temp passthrough to clear old queue
import huey.contrib.djhuey as huey
from huey.contrib.djhuey import HUEY as hueycur
@huey.task()
def fetch_all_albums_for_artist(artist_id: int):
    hueycur.flush()
    pass

@huey.task(context=True)
def download_missing_albums_for_artist(artist_id: int, task: Task = None):
    hueycur.flush()
    pass
