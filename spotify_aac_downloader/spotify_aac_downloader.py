from __future__ import annotations

import logging
from pathlib import Path

from . import __version__
from .constants import X_NOT_FOUND_STRING
from .downloader import Downloader
from ..spotify_library_sync.library_manager.models import Artist, Song

class Config:
    urls: tuple[str] = []
    final_path: Path = "./Spotify"
    temp_path: Path = "./temp"
    cookies_location: Path = "./cookies.txt"
    wvd_location: Path = "./device.wvd"
    config_location: Path = "./config.json"
    ffmpeg_location: str = "ffmpeg"
    aria2c_location: str = "aria2c"
    template_folder_album: str = "{album_artist}/{album}"
    template_folder_compilation: str = "Compilations/{album}"
    template_file_single_disc: str = "{track:02d} {title}"
    template_file_multi_disc: str = "{disc}-{track:02d} {title}"
    download_mode: str = "ytdlp"
    exclude_tags: str = None
    truncate: int = 120
    log_level: str = "INFO"
    premium_quality: bool = True
    lrc_only: bool = False
    no_lrc: bool = False
    save_cover: bool = False
    overwrite: bool = False
    print_exceptions: bool = True
    url_txt: bool = None

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
    downloader = Downloader(**locals())
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
    error_count = 0
    for url_index, url in enumerate(config.urls, start=1):
        current_url = f"URL {url_index}/{len(config.urls)}"
        try:
            logger.debug(f'({current_url}) Checking "{url}"')
            download_queue.append(downloader.get_download_queue(url))
        except Exception:
            error_count += 1
            logger.error(
                f'({current_url}) Failed to check "{url}"',
                exc_info=config.print_exceptions,
            )
    for queue_item_index, queue_item in enumerate(download_queue, start=1):
        for track_index, track in enumerate(queue_item, start=1):
            current_track = f"Track {track_index}/{len(queue_item)} from URL {queue_item_index}/{len(download_queue)}"
            try:
                logger.info(f'({current_track}) Downloading "{track["name"]}"')
                logger.info(track)
                logger.info(track["id"])
                track_id = track["id"]
                logger.debug("Getting metadata")
                gid = downloader.uri_to_gid(track_id)
                metadata = downloader.get_metadata(gid)
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
    logger.info(f"Done ({error_count} error(s))")
