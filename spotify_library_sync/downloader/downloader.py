import functools
import json
import re

from library_manager.models import Album, Artist, ContributingArtist, DownloadHistory, Song, TrackedPlaylist
from . import utils

from spotdl.utils.spotify import SpotifyClient

class Downloader:
    def __init__(self, spotipy_client: SpotifyClient):
        self.spotipy_client = spotipy_client

    def get_artist_albums(self, artist_gid: str) -> list[Album]:
        """Get all albums (including EPs and Singles) for this artist

        Args:
            artist_gid (str): The artist GID as supplied by Spotify

        Returns:
            list[str]: an array of urls to each album for the artist
        """
        artist = Artist.objects.get(gid=artist_gid)
        albums_to_create_or_update: list[dict] = []
        artist_uri = utils.gid_to_uri(artist_gid)

        album_iterator = self.spotipy_client.artist_albums(artist_uri, limit=50)

        while album_iterator is not None:
            for album in album_iterator['items']:
                new_or_updated_album_data: dict = {
                    'spotify_gid': utils.uri_to_gid(album['id']),
                    'artist': artist,
                    'spotify_uri': album['uri'],
                    'total_tracks': album['total_tracks'],
                    'name': album['name'],
                }

                albums_to_create_or_update.append(new_or_updated_album_data)
            
            album_iterator = self.spotipy_client.next(album_iterator)

        if len(albums_to_create_or_update) == 0:
            return []

        albums: list[Artist] = Album.objects.bulk_create(
            [Album(**album) for album in albums_to_create_or_update],
            update_conflicts=True,
            unique_fields=["spotify_gid"],
            update_fields=albums_to_create_or_update[0].keys(),
        )
        return albums
    
    def get_track(self, track_id: str) -> dict:
        return self.spotipy_client.track(track_id)

    @functools.lru_cache()
    def get_album(self, album_id: str) -> dict:
        album = self.spotipy_client.album(album_id)
        album_track_iterator = self.spotipy_client.next(album["tracks"])

        while album_track_iterator is not None:
            album["tracks"]["items"].extend(album_track_iterator["items"])
            album_track_iterator = self.spotipy_client.next(album_track_iterator)
        return album
    
    def get_playlist(self, playlist_id: str) -> dict:
        playlist = self.spotipy_client.playlist(playlist_id)
        playlist_iterator = self.spotipy_client.next(playlist["tracks"])

        while playlist_iterator is not None:
            playlist["tracks"]["items"].extend(playlist_iterator["items"])
            playlist_iterator = self.spotipy_client.next(playlist_iterator)
        return playlist
    
    def get_download_queue(self, url: str) -> list[dict]:
        uri = re.search(r"(\w{22})", url).group(1)
        download_queue = []
        if "album" in url:
            download_queue.extend(self.get_album(uri)["tracks"]["items"])
        elif "track" in url:
            download_queue.append(self.get_track(uri))
        elif "playlist" in url:
            raw_playlist = self.get_playlist(uri)["tracks"]["items"]
            for i in raw_playlist:
                i['track']['added_at'] = i['added_at']
            download_queue.extend(
                [i["track"] for i in raw_playlist]
            )
        else:
            raise Exception("Not a valid Spotify URL")
        return download_queue
    
    def get_song_core_info(self, metadata: dict) -> str:
        return {
            'song_gid': utils.uri_to_gid(metadata['id']),
            'song_name': metadata['name'],
        }
