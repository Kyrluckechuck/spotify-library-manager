# TODO -- this will be a wrapper around spotdl
# spotdl --config
# Provide --cookie-file /something/cookies.txt, if it exists
# Come up with system to:
# - Create & save artists that contributed to playlist/album
# - Mark songs as downloaded
# - If playlist starts with spotify:album:, mark album as downloaded
# - Fetch music from playlist API to validate if it needs to be downloaded
from __future__ import annotations, division

import asyncio
from argparse import Namespace
import logging
import pathlib
import traceback
from pymediainfo import MediaInfo

from . import __version__
from . import utils
from .downloader import Downloader
from .default_download_settings import DEFAULT_DOWNLOAD_SETTINGS
from . import spotdl_override
from lib.config_class import Config
from library_manager.models import Album, Artist, ContributingArtist, DownloadHistory, Song, TrackedPlaylist

from django.db.models.functions import Now

from spotdl import Spotdl
from spotdl.download.downloader import Downloader as SpotdlDownloader
from spotdl.types.song import Song as SpotdlSong
from spotdl.utils.config import create_settings
from spotdl.utils.spotify import SpotifyClient
from spotdl.utils.logging import init_logging

class BitrateException(Exception):
    pass
class SpotdlDownloadError(Exception):
    pass

# Apply monkeypatches to Spotdl for compatibility
# See spotdl_override module for more information
Spotdl.__init__ = spotdl_override.__init__
SpotdlDownloader.download_song = spotdl_override.download_song

def update_process_info(config: Config, progress: int):
    if config.process_info is None:
        return
    config.process_info.total_progress = progress
    config.process_info.update(n=0)

def generate_spotdl_settings(config: Config):
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
            spotify_settings["downloader_settings"][key] = DEFAULT_DOWNLOAD_SETTINGS[key]

    if (config.cookies_location):
        spotify_settings["downloader_settings"]["cookie_file"] = config.cookies_location

    if (config.po_token):
        spotify_settings["downloader_settings"]["yt_dlp_args"] = f"--extractor-args \"youtube:player_client=web_music,default;po_token=web_music+{config.po_token}\""

    return spotify_settings

def initiate_logger(log_level: str):
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
        self.logger = initiate_logger(config.log_level)
        self.logger.info(f"SpotdlWrapper Version: {__version__}")

        spotdl_settings = generate_spotdl_settings(config)

        self.spotdl = Spotdl(**spotdl_settings)

        self.spotipy_client = SpotifyClient()
        
        self.downloader = Downloader(self.spotipy_client)
        self.logger.debug("Completed SpotdlWrapper Initialization")

    def execute(
        self,
        config: Config
    ) -> int:
        download_queue = []
        download_queue_urls: list[str] = []
        error_count = 0

        if config.artist_to_fetch is not None:
            # Do not track the artist if it's mass downloaded
            albums = self.downloader.get_artist_albums(config.artist_to_fetch)
            self.logger.info(f"Fetched latest {len(albums)} album(s) for this artist")
            return
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
                if (config.print_exceptions):
                    self.logger.error(traceback.format_exc())

        if len(download_queue) > 0:
            one_queue_increment = (1 / len(download_queue)) * 1000

        for queue_item_index, queue_item in enumerate(download_queue, start=1):
            download_queue_url = download_queue_urls[queue_item_index - 1]
            download_queue_item = DownloadHistory.objects.get_or_create(
                url=download_queue_url,
                completed_at=None,
                defaults={
                    'url': download_queue_url,
                }
            )[0]

            try:
                tracked_playlist = TrackedPlaylist.objects.get(url=download_queue_url)
                # Check this is the playlist has ever been synced
                if tracked_playlist.last_synced_at is not None:
                    playlist_needs_update = False
                    for track_index, track in enumerate(queue_item, start=1):
                        track_added_at = utils.convert_date_string_to_datetime(track['added_at'])
                        if track_added_at > tracked_playlist.last_synced_at:
                            playlist_needs_update = True
                    if not playlist_needs_update:
                        self.logger.info(f"Playlist has no newer tracks than the last time it synced at {tracked_playlist.last_synced_at}, skipping")
                        continue
                    else:
                        self.logger.info(f"Playlist has newer tracks than the last time it synced at {tracked_playlist.last_synced_at}, resyncing")
            except TrackedPlaylist.DoesNotExist:
                tracked_playlist = None

            main_queue_progress = ((queue_item_index - 1) / len(download_queue)) * 1000

            for track_index, track in enumerate(queue_item, start=1):

                # Check if this is a tracked playlist, and if so let's only sync if the track is newer than the last sync
                if tracked_playlist is not None and tracked_playlist.last_synced_at is not None:
                    track_added_at = utils.convert_date_string_to_datetime(track['added_at'])
                    if track_added_at < tracked_playlist.last_synced_at:
                        self.logger.debug('track older than last playlist sync, skipping')
                        continue

                current_track = f"Track {track_index}/{len(queue_item)} from URL {queue_item_index}/{len(download_queue)}"
                download_queue_item.progress = round(track_index / len(queue_item) * 1000, 1)
                download_queue_item.save()

                update_process_info(config, main_queue_progress + round(track_index / len(queue_item), 3) * one_queue_increment)
                try:
                    self.logger.info(f'({current_track}) Downloading "{track["name"]}"')
                    primary_artist = track['artists'][0]
                    other_artists = track['artists'][1:]
                    song = self.downloader.get_song_core_info(track)

                    primary_artist_gid = utils.uri_to_gid(primary_artist['id'])
                    primary_artist_defaults = {
                        'name': primary_artist['name'],
                        'gid': primary_artist_gid,
                    }
                    if config.track_artists:
                        primary_artist_defaults['tracked'] = True
                    
                    db_artist = Artist.objects.update_or_create(
                        gid=primary_artist_gid,
                        defaults=primary_artist_defaults
                    )[0]

                    db_extra_artists = [db_artist]
                    
                    for artist in other_artists:
                        artist_gid = utils.uri_to_gid(artist['id'])
                        db_extra_artists.append(Artist.objects.update_or_create(
                            gid=artist_gid,
                            defaults={
                                'name': artist['name'],
                                'gid': artist_gid,
                            })[0])

                    db_song = Song.objects.update_or_create(
                        gid=song['song_gid'],
                        defaults={
                            'primary_artist': db_artist,
                            'name': song['song_name'],
                            'gid': song['song_gid'],
                        })[0]

                    for artist in db_extra_artists:
                        ContributingArtist.objects.get_or_create(artist=artist, song=db_song)

                    song_success, output_path = self.spotdl.download(SpotdlSong.from_url(track['external_urls']['spotify']))
                    if (song_success is None or output_path is None):
                        self.logger.debug(song_success)
                        self.logger.debug(f"output_path: {output_path}")
                        raise SpotdlDownloadError("Failed to download correctly")
                    
                    # Validate the song is in the correct audio bitrate
                    # Validate premium successfully applied, for example
                    expected_bitrate = 255 if config.cookies_location is not None and config.po_token is not None else 127

                    media_info = MediaInfo.parse(output_path)
                    for track in media_info.tracks:
                        if track.track_type == "Audio":
                            audio_track = track
                            bit_rate = audio_track.bit_rate / 1000
                            break
                    
                    if (audio_track is None or bit_rate < expected_bitrate):
                        # pathlib.Path.unlink(output_path)
                        if audio_track is None:
                            raise BitrateException(f"File was downloaded successfully, but no audio track existed | output_path: {output_path}")
                        raise BitrateException(f"File was downloaded successfully but not in the correct bitrate ({bit_rate} found, but {expected_bitrate} is minimum expected) | output_path: {output_path}")
                except BitrateException as exception:
                    error_count += 1
                    self.logger.error("Critical bitrate exception occurred, halting download queue")
                    self.logger.error(f'({current_track}) Failed to download "{track["name"]}"')
                    self.logger.error(f"exception: {exception}")
                    # Don't count a bitrate exception towards song/album failures since it's likely a misconfiguration problem
                    raise exception
                except SpotdlDownloadError as exception:
                    error_count += 1
                    self.logger.error(f'({current_track}) Failed to download "{track["name"]}"')
                    self.logger.error(f"exception: {exception}")
                    self.logger.error("This track is possibly not available in your region")
                    db_song.failed_count += 1
                    db_song.save()
                except Exception as exception:
                    error_count += 1
                    self.logger.error(f'({current_track}) Failed to download "{track["name"]}"')
                    self.logger.error(f"exception: {exception}")
                    db_song.failed_count += 1
                    db_song.save()
                    if (config.print_exceptions):
                        self.logger.error(traceback.format_exc())

                if track_index == len(queue_item):
                    download_queue_item.completed_at = Now()
                    download_queue_item.save()

                    if download_queue_url.startswith('spotify:album:'):
                        try:
                            album = Album.objects.get(spotify_uri=download_queue_url)
                        except Album.DoesNotExist:
                            album = self.downloader.create_album(download_queue_url, artist)
                        if (album is not None):
                            album.downloaded = True
                            album.save()
                        else:
                            self.logger.warning("Spotify album downloaded but was not expected and could not be created")

                    if tracked_playlist is not None:
                        tracked_playlist.last_synced_at = Now()
                        tracked_playlist.save()

        update_process_info(config, 1000)
        self.logger.info(f"Done ({error_count} error(s))")
        return error_count
