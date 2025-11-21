from typing import Optional

from django.conf import settings

import spotipy

# from huey.api import Task  # Removed for Celery migration
from spotipy.oauth2 import SpotifyClientCredentials

from library_manager.models import Artist

from .downloader import Downloader
from .spotify_auth_helper import get_spotify_oauth_credentials


class SpotifyClient:
    def __init__(self) -> None:
        # Try to use OAuth credentials first (for private playlist access)
        oauth_creds = get_spotify_oauth_credentials()

        if oauth_creds:
            # Use OAuth token for authenticated access (supports private playlists)
            # Pass the access token directly to avoid interactive prompts
            self.sp = spotipy.Spotify(auth=oauth_creds["access_token"])
        else:
            # Fall back to client credentials (public access only)
            client_credentials_manager = SpotifyClientCredentials(
                client_id=getattr(settings, "SPOTIPY_CLIENT_ID", ""),
                client_secret=getattr(settings, "SPOTIPY_CLIENT_SECRET", ""),
            )
            self.sp = spotipy.Spotify(
                client_credentials_manager=client_credentials_manager
            )


def track_artists_in_playlist(playlist_url: str, task_id: Optional[str] = None) -> None:
    """Mark all primary artists in a playlist as tracked."""
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
        from library_manager.validators import extract_spotify_id_from_uri

        # Extract base62 Spotify ID from URI/URL (avoids hex encoding)
        primary_artist_gid = extract_spotify_id_from_uri(primary_artist["id"])
        if not primary_artist_gid:
            print(f"Skipping artist with invalid ID format: {primary_artist['id']}")
            continue

        primary_artist_info = {
            "name": primary_artist["name"],
            "gid": primary_artist_gid,
            "tracked": True,
        }
        if primary_artist_info not in artists_to_track:
            artists_to_track.append(primary_artist_info)

    for artist_info in artists_to_track:
        artist_gid = artist_info["gid"]
        # Get or create artist, handling both hex and base62 GIDs
        try:
            artist = Artist.objects.get(gid=artist_gid)
            # Update existing artist
            artist.name = artist_info["name"]
            artist.tracked = artist_info["tracked"]
            artist.save()
        except Artist.DoesNotExist:
            # Check if artist exists with hex GID (legacy format)
            from . import utils

            hex_gid = utils.uri_to_gid(artist_gid)
            try:
                artist = Artist.objects.get(gid=hex_gid)
                # Found with hex GID - update to base62
                from django.db import connection, transaction

                with transaction.atomic():
                    # Update albums' artist_gid FK column
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "UPDATE albums SET artist_gid = %s WHERE artist_gid = %s",
                            [artist_gid, hex_gid],
                        )
                    # Now safe to update artist's GID
                    artist.gid = artist_gid
                    artist.name = artist_info["name"]
                    artist.tracked = artist_info["tracked"]
                    artist.save()
            except Artist.DoesNotExist:
                # Doesn't exist with either format - create new
                Artist.objects.create(**artist_info)

    print(f"ensured {len(artists_to_track)} artists were tracked")
