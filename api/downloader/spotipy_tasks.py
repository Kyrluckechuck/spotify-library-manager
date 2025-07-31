from django.conf import settings

import spotipy
from huey.api import Task
from spotipy.oauth2 import SpotifyClientCredentials

from library_manager.models import Artist

from . import utils
from .downloader import Downloader

# TODO: Re-add spotdl integration once all dependencies are resolved
# For now, just basic Spotify client functionality


class SpotifyClient:
    def __init__(self) -> None:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=getattr(settings, "SPOTIPY_CLIENT_ID", ""),
            client_secret=getattr(settings, "SPOTIPY_CLIENT_SECRET", ""),
        )
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def track_artists_in_playlist(playlist_url: str, task: Task) -> None:
    # TODO: Implement artist tracking from playlist
    spotipy_client = SpotifyClient()
    downloader = Downloader(spotipy_client.sp)
    playlist = downloader.get_playlist(playlist_url)
    # pp(playlist)
    artists_to_track = []
    for track in playlist["tracks"]["items"]:
        if len(track["track"]["artists"]) == 0:
            print(
                f"Skipping track {track['track']['name']}('{track['track']['uri']}') due to lack of artists"
            )
            print(track["track"])
            continue
        primary_artist = track["track"]["artists"][0]
        if primary_artist["id"] is None:
            print(
                f"Skipping track {track['track']['name']}('{track['track']['uri']}') due to being placeholder artist"
            )
            print(primary_artist)
            continue
        primary_artist_gid = utils.uri_to_gid(primary_artist["id"])
        primary_artist_info = {
            "name": primary_artist["name"],
            "gid": primary_artist_gid,
            "tracked": True,
        }
        if primary_artist_info not in artists_to_track:
            artists_to_track.append(primary_artist_info)

    for artist_info in artists_to_track:
        Artist.objects.update_or_create(gid=artist_info["gid"], defaults=artist_info)[0]

    print(f"ensured {len(artists_to_track)} artists were tracked")
