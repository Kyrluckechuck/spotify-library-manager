"""Artist tasks for the Spotify library manager."""

from typing import Optional

from django.conf import settings
from django.db.models.functions import Now
from django.utils import timezone

from celery_app import app as celery_app  # noqa: F401
from lib.config_class import Config

from .. import helpers
from ..models import (
    ALBUM_GROUPS_TO_IGNORE,
    ALBUM_TYPES_TO_DOWNLOAD,
    Artist,
    DownloadHistory,
)
from .core import (
    TaskCancelledException,
    check_and_update_progress,
    check_if_cancelled,
    check_task_cancellation,
    complete_task,
    create_task_history,
    logger,
    require_download_capability,
    spotdl_wrapper,
    update_task_progress,
)


def fetch_all_albums_for_artist_sync(artist_id: int) -> None:
    """Synchronous wrapper for fetch_all_albums_for_artist - for direct calls."""
    fetch_all_albums_for_artist.delay(artist_id)


def fetch_all_albums_for_artist(self, artist_id: int) -> None:
    task_history = None
    try:
        # Check if artist exists before proceeding
        try:
            artist = Artist.objects.get(id=artist_id)
        except Artist.DoesNotExist:
            logger.warning(f"Artist with ID {artist_id} does not exist. Skipping task.")
            return

        # Create task history record (always create, even without Celery context)
        task_history = create_task_history(
            task_id=self.request.id,
            task_type="FETCH",
            entity_id=artist.gid,
            entity_type="ARTIST",
            task_name="fetch_all_albums_for_artist",
        )
        update_task_progress(
            task_history, 0.0, f"Starting fetch for artist {artist.name}"
        )
        # Mark as running
        task_history.status = "RUNNING"
        task_history.save()

        # Check authentication before proceeding
        require_download_capability(task_history)

        # Check for cancellation before proceeding
        if check_task_cancellation(task_history):
            logger.info(f"Task cancelled for artist {artist.name}")
            return

        downloader_config = Config()
        downloader_config.artist_to_fetch = artist.gid
        downloader_config.urls = []

        # Check for cancellation before major operation
        if check_and_update_progress(
            task_history, 25.0, "Fetching artist albums from Spotify"
        ):
            logger.info(f"Task cancelled during Spotify fetch for artist {artist.name}")
            return

        # Create callback to update task progress during fetch (if task_history exists)
        if task_history:

            def fetch_progress_callback(progress_pct: float, message: str) -> None:
                # Check for cancellation during fetch
                try:
                    check_if_cancelled(self.request.id)
                except TaskCancelledException:
                    logger.info(f"Fetch cancelled by user for artist {artist.name}")
                    raise
                update_task_progress(task_history, progress_pct, message)

            try:
                spotdl_wrapper.execute(
                    downloader_config, task_progress_callback=fetch_progress_callback
                )
            except TaskCancelledException as e:
                logger.info(f"Fetch cancelled: {e}")
                if task_history:
                    task_history.status = "CANCELLED"
                    task_history.error_message = "Cancelled by user"
                    task_history.save()
                return
        else:
            spotdl_wrapper.execute(downloader_config)

        # Final cancellation check before completion
        if check_task_cancellation(task_history):
            logger.info(f"Task cancelled before completion for artist {artist.name}")
            return

        # Update last_synced_at timestamp (metadata sync completed)
        artist.last_synced_at = Now()
        artist.save()

        complete_task(task_history, success=True)

    except Exception as e:
        if task_history:
            complete_task(task_history, success=False, error_message=str(e))
        raise


def update_tracked_artists(self, task_id: Optional[str] = None) -> None:
    all_tracked_artists = Artist.objects.filter(tracked=True).order_by(
        "last_synced_at", "added_at", "id"
    )
    helpers.update_tracked_artists_albums(
        [],
        list(all_tracked_artists),
        priority=None,  # task.priority not available
    )


# Severely throttling automatic playlist download for tracked artists for the time being;
# There is a high likelyhood of being flagged due to high usage at the moment and a new scalable solution needs to be investigated.


def download_missing_tracked_artists(self, task_id: Optional[str] = None) -> None:
    if settings.disable_missing_tracked_artist_download:
        logger.info(
            "Skipping queued missing tracked artists due to disable_missing_tracked_artist_download setting"
        )
        return

    from datetime import timedelta

    twelve_hours_ago = timezone.now() - timedelta(hours=12)
    recently_downloaded_songs = DownloadHistory.objects.filter(
        added_at__gte=twelve_hours_ago
    )
    if recently_downloaded_songs.count() > 250:
        logger.info(
            f"Skipping queued missing tracked artists due to quantity of recent downloads ({recently_downloaded_songs.count()})"
        )
        return
    # Limit to only desired album types (ignoring `appears_on`), and limit results so this won't throttle
    all_tracked_artists = (
        Artist.objects.filter(
            tracked=True,
            album__downloaded=False,
            album__wanted=True,
            album__album_type__in=ALBUM_TYPES_TO_DOWNLOAD,
        )
        .exclude(album__album_group__in=ALBUM_GROUPS_TO_IGNORE)
        .distinct()
        .order_by("last_synced_at", "added_at", "id")[:150]
    )
    helpers.download_missing_tracked_artists(
        [], list(all_tracked_artists), priority=None
    )
