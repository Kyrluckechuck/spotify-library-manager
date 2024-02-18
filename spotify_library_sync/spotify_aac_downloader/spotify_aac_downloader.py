from __future__ import annotations, division

import logging
from pathlib import Path

from requests import JSONDecodeError

from . import __version__
from .constants import X_NOT_FOUND_STRING
from .downloader import Downloader
from library_manager.models import Album, Artist, ContributingArtist, DownloadHistory, Song, TrackedPlaylist

from django.conf import settings
from django.db.models.functions import Now

from huey_monitor.tqdm import ProcessInfo
class Config:

    def __init__(
        self,
        urls: list[str] = [],
        final_path: Path = Path(settings.final_path),
        temp_path: Path = Path(settings.temp_path),
        cookies_location: Path = Path(settings.cookies_location),
        wvd_location: Path = Path(settings.wvd_location),
        ffmpeg_location: str = settings.ffmpeg_location,
        aria2c_location: str = settings.aria2c_location,
        template_artist_folder_album: str = settings.template_artist_folder_album,
        template_folder_album: str = settings.template_folder_album,
        template_folder_compilation: str = settings.template_folder_compilation,
        template_file_single_disc: str = settings.template_file_single_disc,
        template_file_multi_disc: str = settings.template_file_multi_disc,
        download_mode: str = settings.download_mode,
        exclude_tags: str = None,
        truncate: int = settings.truncate,
        log_level: str = settings.log_level,
        premium_quality: bool = settings.premium_quality,
        lrc_only: bool = settings.lrc_only,
        no_lrc: bool = settings.no_lrc,
        save_cover: bool = settings.save_cover,
        overwrite: bool = settings.overwrite,
        print_exceptions: bool = settings.print_exceptions,
        url_txt: bool = None,
        track_artists: bool = False,
        artist_to_fetch: str = None,
        process_info: ProcessInfo = None,
    ):
        self.urls = urls
        self.final_path = final_path
        self.temp_path = temp_path
        self.cookies_location = cookies_location
        self.wvd_location = wvd_location
        self.ffmpeg_location = ffmpeg_location
        self.aria2c_location = aria2c_location
        self.template_artist_folder_album = template_artist_folder_album
        self.template_folder_album = template_folder_album
        self.template_folder_compilation = template_folder_compilation
        self.template_file_single_disc = template_file_single_disc
        self.template_file_multi_disc = template_file_multi_disc
        self.download_mode = download_mode
        self.exclude_tags = exclude_tags
        self.truncate = truncate
        self.log_level = log_level
        self.premium_quality = premium_quality
        self.lrc_only = lrc_only
        self.no_lrc = no_lrc
        self.save_cover = save_cover
        self.overwrite = overwrite
        self.print_exceptions = print_exceptions
        self.url_txt = url_txt
        self.track_artists = track_artists
        self.artist_to_fetch = artist_to_fetch
        self.process_info = process_info

def update_process_info(config: Config, progress: int):
    if config.process_info is None:
        return
    config.process_info.total_progress = progress
    config.process_info.update(n=0)

def main(
    config: Config
):
    logging.basicConfig(
        format="[%(levelname)-8s %(asctime)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(config.log_level)
    logger.debug(f"Version: {__version__}")
    logger.debug("Starting downloader")
    downloader = Downloader(**config.__dict__)
    if not downloader.ffmpeg_location:
        logger.critical(X_NOT_FOUND_STRING.format("FFmpeg", config.ffmpeg_location))
        return
    if config.download_mode == "aria2c" and not downloader.aria2c_location:
        logger.critical(X_NOT_FOUND_STRING.format("aria2c", config.aria2c_location))
        return
    if config.cookies_location is not None and not config.cookies_location.exists():
        logger.critical(X_NOT_FOUND_STRING.format("Cookies", config.cookies_location))
        return
    if not config.wvd_location.exists() and not config.lrc_only:
        logger.critical(X_NOT_FOUND_STRING.format(".wvd file", config.wvd_location))
        return
    if config.url_txt:
        logger.debug("Reading URLs from text files")
        _urls = []
        for queue_item in config.urls:
            with open(queue_item, "r") as f:
                _urls.extend(f.read().splitlines())
        config.urls = tuple(_urls)
    if not config.lrc_only:
        if not config.wvd_location.exists():
            logger.critical(X_NOT_FOUND_STRING.format(".wvd file", config.wvd_location))
            return
        logger.debug("Setting up CDM")
        downloader.setup_cdm()
    logger.debug("Setting up session")
    downloader.initialize_sessions()
    if config.premium_quality and downloader.is_premium == "false":
        logger.critical("Cannot download in premium quality with a free account")
        return
    download_queue = []
    download_queue_urls: list[str] = []
    error_count = 0
    if config.artist_to_fetch is not None:
        # Do not track the artist if it's mass downloaded
        albums = downloader.get_artist_albums(config.artist_to_fetch)
        logger.info(f"Fetched latest {len(albums)} album(s) for this artist")
        return

    for url_index, url in enumerate(config.urls, start=1):
        current_url = f"URL {url_index}/{len(config.urls)}"
        try:
            logger.debug(f'({current_url}) Checking "{url}"')
            download_queue.append(downloader.get_download_queue(url))
            download_queue_urls.append(url)
        except Exception:
            error_count += 1
            logger.error(
                f'({current_url}) Failed to check "{url}"',
                exc_info=config.print_exceptions,
            )

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

        main_queue_progress = ((queue_item_index - 1) / len(download_queue)) * 1000

        for track_index, track in enumerate(queue_item, start=1):
            current_track = f"Track {track_index}/{len(queue_item)} from URL {queue_item_index}/{len(download_queue)}"
            download_queue_item.progress = round(track_index / len(queue_item) * 1000, 1)
            download_queue_item.save()

            update_process_info(config, main_queue_progress + round(track_index / len(queue_item), 3) * one_queue_increment)
            try:
                logger.info(f'({current_track}) Downloading "{track["name"]}"')
                track_id = track["id"]
                logger.debug("Getting metadata")
                gid = downloader.uri_to_gid(track_id)
                try:
                    metadata = downloader.get_metadata(gid)
                except JSONDecodeError:
                    downloader.initialize_sessions()
                    metadata = downloader.get_metadata(gid)
                primary_artist = downloader.get_primary_artist(metadata)
                other_artists = downloader.get_other_artists(metadata, primary_artist['artist_gid'])
                song = downloader.get_song_core_info(metadata)

                primary_artist_defaults = {
                    'name': primary_artist['artist_name'],
                    'gid': primary_artist['artist_gid'],
                }
                if config.track_artists:
                    primary_artist_defaults['tracked'] = True
                db_artist = Artist.objects.update_or_create(
                    gid=primary_artist['artist_gid'],
                    defaults=primary_artist_defaults
                )[0]

                db_extra_artists = [db_artist]
                for artist in other_artists:
                    db_extra_artists.append(Artist.objects.update_or_create(
                        gid=artist['artist_gid'],
                        defaults={
                            'name': artist['artist_name'],
                            'gid': artist['artist_gid'],
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

                # continue
                if metadata.get("has_lyrics"):
                    logger.debug("Getting lyrics")
                    lyrics_unsynced, lyrics_synced = downloader.get_lyrics(track_id)
                else:
                    lyrics_unsynced, lyrics_synced = None, None
                tags = downloader.get_tags(metadata, lyrics_unsynced)
                final_location = downloader.get_final_location(tags)
                lrc_location = downloader.get_lrc_location(final_location)
                cover_location = downloader.get_cover_location(final_location)
                cover_url = downloader.get_cover_url(metadata)
                if config.lrc_only:
                    pass
                elif final_location.exists() and not config.overwrite:
                    logger.warning(
                        f'({current_track}) Track already exists at "{final_location}", skipping'
                    )
                else:
                    logger.debug("Getting file info")
                    file_id = downloader.get_file_id(metadata)
                    if not file_id:
                        logger.error(
                            f"({current_track}) Track not available on Spotify's "
                            "servers and no alternative found, skipping"
                        )
                        continue
                    logger.debug("Getting PSSH")
                    pssh = downloader.get_pssh(file_id)
                    logger.debug("Getting decryption key")
                    decryption_key = downloader.get_decryption_key(pssh)
                    logger.debug("Getting stream URL")
                    stream_url = downloader.get_stream_url(file_id)
                    encrypted_location = downloader.get_encrypted_location(track_id)
                    logger.debug(f'Downloading to "{encrypted_location}"')
                    if config.download_mode == "ytdlp":
                        downloader.download_ytdlp(encrypted_location, stream_url)
                    if config.download_mode == "aria2c":
                        downloader.download_aria2c(encrypted_location, stream_url)
                    fixed_location = downloader.get_fixed_location(track_id)
                    logger.debug(f'Remuxing to "{fixed_location}"')
                    downloader.fixup(decryption_key, encrypted_location, fixed_location)
                    logger.debug("Applying tags")
                    downloader.apply_tags(fixed_location, tags, cover_url)
                    logger.debug(f'Moving to "{final_location}"')
                    downloader.move_to_final_location(fixed_location, final_location)
                    
                if config.no_lrc or not lyrics_synced:
                    pass
                elif lrc_location.exists() and not config.overwrite:
                    logger.debug(
                        f'Synced lyrics already exists at "{lrc_location}", skipping'
                    )
                else:
                    logger.debug(f'Saving synced lyrics to "{lrc_location}"')
                    downloader.save_lrc(lrc_location, lyrics_synced)
                if config.lrc_only or not config.save_cover:
                    pass
                elif cover_location.exists() and not config.overwrite:
                    logger.debug(
                        f'Cover already exists at "{cover_location}", skipping'
                    )
                else:
                    logger.debug(f'Saving cover to "{cover_location}"')
                    downloader.save_cover(cover_location, cover_url)
            except Exception:
                error_count += 1
                logger.error(
                    f'({current_track}) Failed to download "{track["name"]}"',
                    exc_info=config.print_exceptions,
                )
            finally:
                if config.temp_path.exists():
                    logger.debug(f'Cleaning up "{config.temp_path}"')
                    downloader.cleanup_temp_path()
            if track_index == len(queue_item):
                download_queue_item.completed_at = Now()
                download_queue_item.save()

                if download_queue_url.startswith('spotify:album:'):
                    try:
                        album = Album.objects.get(spotify_uri=download_queue_url)
                        album.downloaded = True
                        album.save()
                    except Album.DoesNotExist:
                        print("Spotify album downloaded but was not expected")

                try:
                    tracked_playlist = TrackedPlaylist.objects.get(url=download_queue_url)
                    tracked_playlist.last_synced = Now()
                    tracked_playlist.save()
                except TrackedPlaylist.DoesNotExist:
                    pass

    update_process_info(config, 1000)
    logger.info(f"Done ({error_count} error(s))")
