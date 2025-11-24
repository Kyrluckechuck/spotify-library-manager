"""Periodic tasks for the Spotify library manager."""

from typing import Optional

from celery_app import app as celery_app

from .. import helpers
from ..models import (
    ALBUM_GROUPS_TO_IGNORE,
    ALBUM_TYPES_TO_DOWNLOAD,
    Album,
    TrackedPlaylist,
)
from .core import logger
from .download import download_single_album


@celery_app.task(
    bind=True, name="library_manager.tasks.sync_tracked_playlists"
)  # Scheduled via Celery Beat
def sync_tracked_playlists(self, task_id: Optional[str] = None) -> None:
    all_enabled_playlists = TrackedPlaylist.objects.filter(enabled=True).order_by(
        "last_synced_at", "id"
    )
    helpers.enqueue_playlists(
        list(all_enabled_playlists), priority=None
    )  # task.priority not available


@celery_app.task(
    bind=True, name="library_manager.tasks.queue_missing_albums_for_tracked_artists"
)  # Scheduled via Celery Beat - Every hour
def queue_missing_albums_for_tracked_artists(self) -> None:
    """
    Periodically find tracked artists with missing music and queue downloads.

    Finds up to 300 albums that are marked as wanted but not yet downloaded
    from tracked artists, and queues them for download.
    """
    try:
        logger.info("Starting periodic queue of missing albums for tracked artists")

        # Find all missing albums for tracked artists
        missing_albums = (
            Album.objects.filter(
                artist__tracked=True,
                downloaded=False,
                wanted=True,
                album_type__in=ALBUM_TYPES_TO_DOWNLOAD,
            )
            .exclude(album_group__in=ALBUM_GROUPS_TO_IGNORE)
            .order_by("id")[:300]
        )

        if not missing_albums.exists():
            logger.info(
                "No missing albums found for tracked artists to queue for download"
            )
            return

        queued_count = 0
        for album in missing_albums:
            try:
                download_single_album.delay(album.id)
                queued_count += 1
            except Exception as e:
                logger.warning(f"Failed to queue album {album.name} ({album.id}): {e}")

        logger.info(
            f"Queued {queued_count} missing albums from tracked artists for download"
        )

    except Exception as e:
        logger.error(
            f"Error in queue_missing_albums_for_tracked_artists: {e}", exc_info=True
        )
