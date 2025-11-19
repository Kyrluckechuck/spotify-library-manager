"""
SpotDL wrapper for downloading music from Spotify playlists and albums.

Handles:
- Creating and saving artists that contributed to playlist/album
- Marking songs as downloaded
- Album download tracking
- Playlist sync validation
"""

from __future__ import annotations, division

import asyncio
import logging
import traceback
from argparse import Namespace
from typing import Any

from django.db.models.functions import Now

from lib.config_class import Config
from pymediainfo import MediaInfo
from spotdl import Spotdl
from spotdl.download.downloader import Downloader as SpotdlDownloader
from spotdl.types.song import Song as SpotdlSong
from spotdl.utils.config import create_settings
from spotdl.utils.logging import init_logging
from spotdl.utils.spotify import SpotifyClient

from library_manager.models import (
    Album,
    Artist,
    ContributingArtist,
    DownloadHistory,
    Song,
    TrackedPlaylist,
)

from . import __version__, spotdl_override, utils
from .default_download_settings import DEFAULT_DOWNLOAD_SETTINGS
from .downloader import Downloader
from .premium_detector import PremiumDetector, PremiumStatus


class BitrateException(Exception):
    pass


class SpotdlDownloadError(Exception):
    pass


class PremiumExpiredException(Exception):
    """Raised when premium status expires during download operation."""

    pass


# Apply monkeypatches to Spotdl for compatibility
# See spotdl_override module for more information
Spotdl.__init__ = spotdl_override.__init__
SpotdlDownloader.download_song = spotdl_override.download_song


def generate_spotdl_settings(config: Config) -> Any:
    spotify_settings, downloader_settings, _ = create_settings(Namespace(config=False))
    del spotify_settings["auth_token"]
    del spotify_settings["max_retries"]
    del spotify_settings["use_cache_file"]
    spotify_settings["downloader_settings"] = downloader_settings

    spotify_settings["downloader_settings"]["log_level"] = config.log_level

    for key in DEFAULT_DOWNLOAD_SETTINGS.keys():
        if key in spotify_settings:
            spotify_settings[key] = DEFAULT_DOWNLOAD_SETTINGS[key]

    for key in DEFAULT_DOWNLOAD_SETTINGS.keys():
        if key in spotify_settings["downloader_settings"]:
            spotify_settings["downloader_settings"][key] = DEFAULT_DOWNLOAD_SETTINGS[
                key
            ]

    if config.cookies_location:
        spotify_settings["downloader_settings"]["cookie_file"] = config.cookies_location

    if config.po_token:
        spotify_settings["downloader_settings"][
            "yt_dlp_args"
        ] = f'--extractor-args "youtube:player_client=web_music,default;po_token=web_music+{config.po_token}"'

    return spotify_settings


def initiate_logger(log_level: str) -> logging.Logger:
    logging.basicConfig(
        format="[%(levelname)-8s %(asctime)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    init_logging(log_level)

    return logger


class SpotdlWrapper:
    def __init__(self, config: Config):
        log_level = config.log_level or "INFO"
        self.logger = initiate_logger(log_level)
        self.logger.info(f"SpotdlWrapper Version: {__version__}")

        spotdl_settings = generate_spotdl_settings(config)

        # Ensure we have a valid event loop and reuse an existing set loop when present
        try:
            # Prefer the currently running loop when available
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop; try to reuse a previously set loop without emitting deprecation warnings
            try:
                import warnings

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", DeprecationWarning)
                    loop = asyncio.get_event_loop_policy().get_event_loop()
                if loop.is_closed():
                    raise RuntimeError("Event loop is closed")
            except Exception:
                # No valid loop exists; create and set a fresh one for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

        # Pass the event loop to Spotdl initialization
        spotdl_settings["loop"] = loop
        self.spotdl = Spotdl(**spotdl_settings)

        self.spotipy_client = SpotifyClient()

        self.downloader = Downloader(self.spotipy_client)

        # Initialize premium detector for quality validation
        self.premium_detector = PremiumDetector(
            cookies_file=config.cookies_location, po_token=config.po_token
        )
        try:
            self.premium_status = self.premium_detector.detect_premium_status()
        except Exception as e:
            self.logger.warning(f"Premium detection failed during initialization: {e}")
            # Create a default free status if detection fails
            self.premium_status = PremiumStatus(
                is_premium=False,
                confidence=0.0,
                detection_method="initialization_failed",
            )

        # Verify premium access at startup to catch expired credentials early
        try:
            has_access, message, _ = (
                self.premium_detector.verify_premium_access_at_startup()
            )
            if has_access:
                self.logger.info(f"✓ Premium access verified: {message}")
            else:
                self.logger.warning(f"⚠ Premium access verification failed: {message}")
                # Update premium status based on startup verification
                if not has_access:
                    self.premium_status = PremiumStatus(
                        is_premium=False,
                        confidence=0.9,
                        detection_method="startup_verification_failed",
                        error_message=message,
                    )
        except Exception as e:
            self.logger.warning(f"Startup premium verification failed: {e}")

        self.logger.debug("Completed SpotdlWrapper Initialization")

    def execute(self, config: Config, task_progress_callback=None) -> int:
        download_queue = []
        download_queue_urls: list[str] = []
        error_count = 0

        if config.artist_to_fetch is not None:
            # Do not track the artist if it's mass downloaded
            albums = self.downloader.get_artist_albums(config.artist_to_fetch)
            self.logger.info(f"Fetched latest {len(albums)} album(s) for this artist")
            return 0
        for url_index, url in enumerate(config.urls, start=1):
            current_url = f"URL {url_index}/{len(config.urls)}"
            try:
                self.logger.info(f'({current_url}) Checking "{url}"')
                download_queue.append(self.downloader.get_download_queue(url=url))
                download_queue_urls.append(url)
            except Exception as exception:
                error_count += 1
                self.logger.error(f'({current_url}) Failed to check "{url}"')
                self.logger.error(f"exception: {exception}")
                if config.print_exceptions:
                    self.logger.error(traceback.format_exc())

                # Handle (gracefully) songs that no longer exist (at all) with Spotify
                if (
                    "too many 404 error responses" in str(exception)
                    or "Track no longer exists" in str(exception)
                ) and (
                    url.startswith("spotify:track:")
                    or url.startswith("https://open.spotify.com/track")
                ):
                    from library_manager.validators import extract_spotify_id_from_uri

                    # Extract Spotify ID from URL
                    track_uri = (
                        url.split("spotify:track:", 1)[1]
                        if "spotify:track:" in url
                        else url.split("/track/", 1)[1].split("?")[0]
                    )
                    song_gid = extract_spotify_id_from_uri(track_uri)

                    if not song_gid:
                        self.logger.warning(
                            f"Failed to extract Spotify ID from URL: {url}"
                        )
                        continue

                    try:
                        # Try to find song by base62 ID (new format)
                        db_song = Song.objects.get(gid=song_gid)
                    except Song.DoesNotExist:
                        # Fall back to hex GID (legacy format) during migration
                        hex_gid = utils.uri_to_gid(song_gid)
                        try:
                            db_song = Song.objects.get(gid=hex_gid)
                        except Song.DoesNotExist:
                            self.logger.warning(
                                f"Song not found in database: {song_gid} (or {hex_gid})"
                            )
                            continue

                    db_song.increment_failed_count()

        if len(download_queue) > 0:
            one_queue_increment = (1 / len(download_queue)) * 1000

        for queue_item_index, queue_item in enumerate(download_queue, start=1):
            download_queue_url = download_queue_urls[queue_item_index - 1]
            download_queue_item = DownloadHistory.objects.get_or_create(
                url=download_queue_url,
                completed_at=None,
                defaults={
                    "url": download_queue_url,
                },
            )[0]

            try:
                tracked_playlist = TrackedPlaylist.objects.get(url=download_queue_url)

                if config.force_playlist_resync:
                    tracked_playlist.last_synced_at = None
                    tracked_playlist.save()
                # Check if this playlist has ever been synced
                if tracked_playlist.last_synced_at is not None:
                    playlist_needs_update = False
                    for track_index, track in enumerate(queue_item, start=1):
                        track_added_at = utils.convert_date_string_to_datetime(
                            track["added_at"]
                        )
                        if track_added_at > tracked_playlist.last_synced_at:
                            playlist_needs_update = True
                    if not playlist_needs_update:
                        self.logger.info(
                            f"Playlist has no newer tracks than the last time it synced at {tracked_playlist.last_synced_at}, skipping"
                        )
                        continue
                    else:
                        self.logger.info(
                            f"Playlist has newer tracks than the last time it synced at {tracked_playlist.last_synced_at}, resyncing"
                        )
            except TrackedPlaylist.DoesNotExist:
                tracked_playlist = None

            main_queue_progress = ((queue_item_index - 1) / len(download_queue)) * 1000

            for track_index, track in enumerate(queue_item, start=1):

                # Check if this is a tracked playlist, and if so let's only sync if the track is newer than the last sync
                if (
                    tracked_playlist is not None
                    and tracked_playlist.last_synced_at is not None
                ):
                    track_added_at = utils.convert_date_string_to_datetime(
                        track["added_at"]
                    )
                    if track_added_at < tracked_playlist.last_synced_at:
                        self.logger.debug(
                            "track older than last playlist sync, skipping"
                        )
                        continue

                current_track = f"Track {track_index}/{len(queue_item)} from URL {queue_item_index}/{len(download_queue)}"
                download_queue_item.progress = round(
                    track_index / len(queue_item) * 1000, 1
                )
                download_queue_item.save()

                # Periodic task progress updates every 5 songs
                if task_progress_callback and track_index % 5 == 0:
                    progress_pct = (
                        main_queue_progress
                        + (track_index / len(queue_item)) * one_queue_increment
                    ) / 10
                    task_progress_callback(
                        progress_pct,
                        f"Downloaded {track_index}/{len(queue_item)} songs from queue {queue_item_index}/{len(download_queue)}",
                    )

                try:
                    self.logger.info(f'({current_track}) Downloading "{track["name"]}"')
                    primary_artist = track["artists"][0]
                    other_artists = track["artists"][1:]
                    song = self.downloader.get_song_core_info(track)

                    from library_manager.validators import extract_spotify_id_from_uri

                    # Extract base62 Spotify ID from URI/URL (avoids hex encoding)
                    primary_artist_gid = extract_spotify_id_from_uri(
                        primary_artist["id"]
                    )
                    if not primary_artist_gid:
                        raise ValueError(
                            f"Invalid Spotify artist ID format: {primary_artist['id']}"
                        )

                    # Get or create artist, handling both hex and base62 GIDs
                    # to avoid duplicates during migration
                    try:
                        db_artist = Artist.objects.get(gid=primary_artist_gid)
                    except Artist.DoesNotExist:
                        # Check if artist exists with hex GID (legacy format)
                        hex_gid = utils.uri_to_gid(primary_artist_gid)
                        try:
                            db_artist = Artist.objects.get(gid=hex_gid)
                            # Found with hex GID - update to base62
                            # Must update albums' FK first to avoid constraint violation
                            from django.db import connection, transaction

                            with transaction.atomic():
                                # Update albums' artist_gid FK column
                                with connection.cursor() as cursor:
                                    cursor.execute(
                                        "UPDATE albums SET artist_gid = %s WHERE artist_gid = %s",
                                        [primary_artist_gid, hex_gid],
                                    )
                                # Now safe to update artist's GID
                                db_artist.gid = primary_artist_gid
                                db_artist.name = primary_artist["name"]
                                if config.track_artists:
                                    db_artist.tracked = True
                                db_artist.save()
                        except Artist.DoesNotExist:
                            # Doesn't exist with either format - create new
                            primary_artist_defaults = {
                                "name": primary_artist["name"],
                                "gid": primary_artist_gid,
                            }
                            if config.track_artists:
                                primary_artist_defaults["tracked"] = True
                            db_artist = Artist.objects.create(**primary_artist_defaults)

                    db_extra_artists = [db_artist]

                    for artist in other_artists:
                        # Extract base62 Spotify ID from URI/URL (avoids hex encoding)
                        artist_gid = extract_spotify_id_from_uri(artist["id"])
                        if not artist_gid:
                            raise ValueError(
                                f"Invalid Spotify artist ID format: {artist['id']}"
                            )

                        # Get or create artist, handling both hex and base62 GIDs
                        try:
                            db_extra_artist = Artist.objects.get(gid=artist_gid)
                        except Artist.DoesNotExist:
                            # Check if artist exists with hex GID (legacy format)
                            hex_gid = utils.uri_to_gid(artist_gid)
                            try:
                                db_extra_artist = Artist.objects.get(gid=hex_gid)
                                # Found with hex GID - update to base62
                                # Must update albums' FK first to avoid constraint violation
                                from django.db import connection, transaction

                                with transaction.atomic():
                                    # Update albums' artist_gid FK column
                                    with connection.cursor() as cursor:
                                        cursor.execute(
                                            "UPDATE albums SET artist_gid = %s WHERE artist_gid = %s",
                                            [artist_gid, hex_gid],
                                        )
                                    # Now safe to update artist's GID
                                    db_extra_artist.gid = artist_gid
                                    db_extra_artist.name = artist["name"]
                                    db_extra_artist.save()
                            except Artist.DoesNotExist:
                                # Doesn't exist with either format - create new
                                db_extra_artist = Artist.objects.create(
                                    name=artist["name"],
                                    gid=artist_gid,
                                )

                        db_extra_artists.append(db_extra_artist)

                    # Get or create song, handling both hex and base62 GIDs
                    song_gid = song["song_gid"]
                    try:
                        db_song = Song.objects.get(gid=song_gid)
                        # Update existing song
                        db_song.primary_artist = db_artist
                        db_song.name = song["song_name"]
                        db_song.save()
                    except Song.DoesNotExist:
                        # Check if song exists with hex GID (legacy format)
                        hex_gid = utils.uri_to_gid(song_gid)
                        try:
                            db_song = Song.objects.get(gid=hex_gid)
                            # Found with hex GID - update to base62
                            db_song.gid = song_gid
                            db_song.primary_artist = db_artist
                            db_song.name = song["song_name"]
                            db_song.save()
                        except Song.DoesNotExist:
                            # Doesn't exist with either format - create new
                            db_song = Song.objects.create(
                                gid=song_gid,
                                primary_artist=db_artist,
                                name=song["song_name"],
                            )

                    for artist in db_extra_artists:
                        ContributingArtist.objects.get_or_create(
                            artist=artist, song=db_song
                        )

                    song_success, output_path = self.spotdl.download(
                        SpotdlSong.from_url(track["external_urls"]["spotify"])
                    )
                    if song_success is None or output_path is None:
                        self.logger.debug(song_success)
                        self.logger.debug(f"output_path: {output_path}")
                        raise SpotdlDownloadError("Failed to download correctly")

                    # Validate the song is in the correct audio bitrate using premium detection
                    spotify_url = track["external_urls"]["spotify"]

                    # Get actual available qualities for this specific song
                    available_qualities = (
                        self.premium_detector.get_song_available_qualities(spotify_url)
                    )
                    max_available = (
                        max([q[0] for q in available_qualities])
                        if available_qualities
                        else 128
                    )

                    # Set expectation based on premium status AND song availability
                    if (
                        self.premium_status.is_premium
                        and self.premium_status.confidence > 0.7
                    ):
                        expected_bitrate = min(
                            255, max_available
                        )  # Premium: up to 256kbps or song max
                    else:
                        expected_bitrate = min(
                            127, max_available
                        )  # Free: up to 128kbps or song max

                    media_info = MediaInfo.parse(output_path)
                    audio_track = None
                    bit_rate = 0
                    for media_track in media_info.tracks:
                        if media_track.track_type == "Audio":
                            audio_track = media_track
                            bit_rate = audio_track.bit_rate / 1000
                            break

                    if audio_track is not None and bit_rate > 0:
                        db_song.bitrate = bit_rate
                        db_song.set_file_path(output_path)
                        db_song.downloaded = True
                        db_song.save()
                    if audio_track is None or bit_rate < expected_bitrate:
                        # pathlib.Path.unlink(output_path)
                        if audio_track is None:
                            raise BitrateException(
                                f"File was downloaded successfully, but no audio track existed | output_path: {output_path}"
                            )
                        # Check if this indicates premium expiry
                        # Uses 240kbps threshold (default) and re-validates account status if low
                        is_expired, expiry_reason = (
                            self.premium_detector.is_premium_expired(
                                downloaded_bitrate=int(bit_rate),
                            )
                        )

                        error_msg = (
                            f"File was downloaded successfully but not in the correct bitrate "
                            f"({bit_rate} found, but {expected_bitrate} is minimum expected) | "
                            f"output_path: {output_path}"
                        )

                        if is_expired:
                            error_message = (
                                f"🚨 PREMIUM EXPIRED: {expiry_reason} | "
                                f"Available qualities for this song: {available_qualities} | "
                                f"Your YouTube Music cookies or po_token have expired. "
                                f"Please refresh your authentication to continue downloading."
                            )
                            self.logger.error(error_message)
                            # Abort the entire task - don't continue with degraded quality
                            raise PremiumExpiredException(error_message)
                        else:
                            self.logger.error(error_msg)
                            self.logger.info(
                                f"Premium status: {self.premium_status.is_premium} "
                                f"(confidence: {self.premium_status.confidence}) | "
                                f"Available qualities: {available_qualities}"
                            )
                except PremiumExpiredException:
                    # Re-raise to abort the entire download task
                    raise
                except SpotdlDownloadError as exception:
                    error_count += 1
                    self.logger.error(
                        f'({current_track}) Failed to download "{db_song.name}"'
                    )
                    self.logger.error(f"Exception: {exception}")
                    self.logger.error(
                        "This track is possibly not available in your region"
                    )
                    # Don't infinitely retry missing songs
                    db_song.increment_failed_count()
                except Exception as exception:
                    error_count += 1
                    self.logger.error(
                        f'({current_track}) Failed to download "{db_song.name}"'
                    )
                    self.logger.error(f"General Exception: {exception}")
                    db_song.failed_count += 1
                    db_song.save()
                    if config.print_exceptions:
                        self.logger.error(traceback.format_exc())
                finally:
                    # Clear any errors from the persisted object, otherwise it will continue printing old failures
                    if len(self.spotdl.downloader.errors) > 0:
                        self.spotdl.downloader.errors.clear()

                if track_index == len(queue_item):
                    download_queue_item.completed_at = Now()
                    download_queue_item.save()

                    # Final progress update for this queue
                    if task_progress_callback:
                        progress_pct = (main_queue_progress + one_queue_increment) / 10
                        task_progress_callback(
                            progress_pct,
                            f"Completed queue {queue_item_index}/{len(download_queue)} ({len(queue_item)} songs)",
                        )

                    if download_queue_url.startswith("spotify:album:"):
                        try:
                            album = Album.objects.get(spotify_uri=download_queue_url)
                        except Album.DoesNotExist:
                            album = None
                        if album is not None:
                            album.downloaded = True
                            album.save()
                        else:
                            self.logger.warning(
                                "Spotify album downloaded but was not expected and could not be created"
                            )

                    if tracked_playlist is not None:
                        tracked_playlist.last_synced_at = Now()
                        tracked_playlist.save()

        self.logger.info(f"Done ({error_count} error(s))")
        return error_count
