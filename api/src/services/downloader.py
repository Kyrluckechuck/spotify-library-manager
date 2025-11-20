# pylint: disable=R1705  # allow explicit elif after return for clarity
import re

from ..graphql_types.models import MutationResult
from .album import AlbumService
from .artist import ArtistService
from .playlist import PlaylistService


class DownloaderService:
    def __init__(self) -> None:
        self.playlist_service = PlaylistService()
        self.artist_service = ArtistService()
        self.album_service = AlbumService()

    async def download_url(
        self, url: str, auto_track_artists: bool = False
    ) -> MutationResult:
        """
        Download content from a Spotify URL/URI.
        Supports playlists, artists, albums, and tracks.
        """
        try:
            # Normalize the URL/URI
            normalized_url = self._normalize_spotify_url(url)

            # Determine the type of content
            content_type = self._get_content_type(normalized_url)

            if content_type == "playlist":
                return await self._handle_playlist_download(
                    normalized_url, auto_track_artists
                )
            elif content_type == "artist":
                return await self._handle_artist_download(normalized_url)
            elif content_type == "album":
                return await self._handle_album_download(normalized_url)
            elif content_type == "track":
                return await self._handle_track_download(normalized_url)
            else:
                return MutationResult(
                    success=False,
                    message=f"Unsupported Spotify content type: {content_type}",
                )

        except Exception as e:
            return MutationResult(
                success=False, message=f"Failed to download URL: {str(e)}"
            )

    def _normalize_spotify_url(self, url: str) -> str:
        """Convert various Spotify URL formats to a standard format."""
        # Handle spotify: URIs
        if url.startswith("spotify:"):
            return url

        # Handle web URLs
        if "open.spotify.com" in url:
            # Extract the path and convert to URI format
            match = re.search(r"open\.spotify\.com/([^/?]+)/([^/?]+)", url)
            if match:
                content_type, content_id = match.groups()
                return f"spotify:{content_type}:{content_id}"

        return url

    def _get_content_type(self, url: str) -> str:
        """Determine the type of Spotify content from URL/URI."""
        if "playlist" in url:
            return "playlist"
        if "artist" in url:
            return "artist"
        if "album" in url:
            return "album"
        if "track" in url:
            return "track"
        return "unknown"

    async def _handle_playlist_download(
        self, playlist_url: str, auto_track_artists: bool
    ) -> MutationResult:
        """Handle playlist download and tracking."""
        try:
            # Extract playlist ID from URL
            playlist_id = self._extract_id_from_url(playlist_url)

            # Create or update playlist
            playlist = await self.playlist_service.track_playlist(
                playlist_id=playlist_id, auto_track_artists=auto_track_artists
            )

            return MutationResult(
                success=True,
                message=f"Successfully started tracking playlist: {playlist.name}",
                playlist=playlist,
            )
        except Exception as e:
            return MutationResult(
                success=False, message=f"Failed to track playlist: {str(e)}"
            )

    async def _handle_artist_download(self, artist_url: str) -> MutationResult:
        """Handle artist download and tracking."""
        try:
            # Extract artist ID from URL
            artist_id = self._extract_id_from_url(artist_url)

            # Sync artist
            artist = await self.artist_service.sync_artist(artist_id)

            return MutationResult(
                success=True,
                message=f"Successfully synced artist: {artist.name}",
                artist=artist,
            )
        except Exception as e:
            return MutationResult(
                success=False, message=f"Failed to sync artist: {str(e)}"
            )

    async def _handle_album_download(self, album_url: str) -> MutationResult:
        """Handle album download."""
        try:
            # Extract album ID from URL
            album_id = self._extract_id_from_url(album_url)

            # Download album
            album = await self.album_service.download_album(album_id)

            return MutationResult(
                success=True,
                message=f"Successfully started downloading album: {album.name}",
                album=album,
            )
        except Exception as e:
            return MutationResult(
                success=False, message=f"Failed to download album: {str(e)}"
            )

    async def _handle_track_download(self, track_url: str) -> MutationResult:
        """Handle track download by fetching track metadata and downloading its album."""
        try:
            from asgiref.sync import sync_to_async

            # Extract track ID from URL
            track_id = self._extract_id_from_url(track_url)

            # Fetch track metadata from Spotify to get album ID
            def get_track_album_id() -> tuple[str, str]:
                from downloader.downloader import Downloader
                from spotdl.utils.spotify import SpotifyClient

                # Create Spotify client and downloader
                spotify_client = SpotifyClient()
                downloader = Downloader(spotify_client)

                # Get track metadata (includes artist, name, ISRC, album info)
                track_data = downloader.get_track(track_id)

                if not track_data or "album" not in track_data:
                    raise ValueError(f"Track {track_id} has no album data")

                album_id = track_data["album"]["id"]
                track_name = track_data["name"]
                return album_id, track_name

            album_id, track_name = await sync_to_async(get_track_album_id)()

            # Download the album containing this track
            album = await self.album_service.download_album(album_id)

            return MutationResult(
                success=True,
                message=f"Successfully started downloading track: {track_name} (from album: {album.name})",
                album=album,
            )
        except Exception as e:
            return MutationResult(
                success=False, message=f"Failed to download track: {str(e)}"
            )

    def _extract_id_from_url(self, url: str) -> str:
        """Extract the ID from a Spotify URL/URI."""
        # Handle spotify: URIs
        if url.startswith("spotify:"):
            parts = url.split(":")
            if len(parts) >= 3:
                return parts[-1]

        # Handle web URLs
        match = re.search(r"/([a-zA-Z0-9]+)(?:\?|$)", url)
        if match:
            return match.group(1)

        raise ValueError(f"Could not extract ID from URL: {url}")


# Create service instance
downloader_service = DownloaderService()
