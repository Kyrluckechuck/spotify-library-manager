# pylint: disable=R1705  # allow explicit elif after return for clarity
# pylint: disable=R0911  # allow many return statements for routing logic
import re

from ..graphql_types.models import MutationResult
from .album import AlbumService
from .artist import ArtistService
from .playlist import PlaylistService
from .spotify_validation import validate_spotify_resource_async


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

            # Validate that the resource exists on Spotify before queueing
            validation = await validate_spotify_resource_async(normalized_url)
            if not validation.valid:
                return MutationResult(
                    success=False,
                    message=validation.error_message or "Invalid Spotify URL",
                )

            # Determine the type of content
            content_type = self._get_content_type(normalized_url)

            if content_type == "playlist":
                return await self._handle_playlist_download(
                    normalized_url, auto_track_artists, validation.resource_name
                )
            elif content_type == "artist":
                return await self._handle_artist_download(normalized_url)
            elif content_type == "album":
                return await self._handle_album_download(
                    normalized_url, validation.resource_name
                )
            elif content_type == "track":
                return await self._handle_track_download(
                    normalized_url, validation.resource_name
                )
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
        self,
        playlist_url: str,
        auto_track_artists: bool,
        playlist_name: str | None = None,
    ) -> MutationResult:
        """Handle one-time playlist download (without tracking)."""
        from asgiref.sync import sync_to_async

        from library_manager.tasks import download_playlist

        try:
            # Queue the download task directly - no need to save playlist to DB
            await sync_to_async(download_playlist.delay)(
                playlist_url=playlist_url,
                tracked=auto_track_artists,  # Whether to track artists found in playlist
                force_playlist_resync=False,
            )

            if playlist_name:
                message = f"Started downloading playlist: {playlist_name}"
            else:
                message = "Started downloading playlist"

            return MutationResult(success=True, message=message)
        except Exception as e:
            return MutationResult(
                success=False, message=f"Failed to download playlist: {str(e)}"
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

    async def _handle_album_download(
        self, album_url: str, album_name: str | None = None
    ) -> MutationResult:
        """Handle album download."""
        try:
            # Extract album ID from URL
            album_id = self._extract_id_from_url(album_url)

            # Download album
            album = await self.album_service.download_album(album_id)

            # Use validated name if album object has placeholder name
            display_name = (
                album_name if album.name == "Download queued..." else album.name
            )

            return MutationResult(
                success=True,
                message=f"Successfully started downloading album: {display_name}",
                album=album,
            )
        except Exception as e:
            return MutationResult(
                success=False, message=f"Failed to download album: {str(e)}"
            )

    async def _handle_track_download(
        self, track_url: str, track_name: str | None = None
    ) -> MutationResult:
        """Handle track download by queueing a Celery task."""
        try:
            from asgiref.sync import sync_to_async

            from library_manager.tasks import download_single_track

            # Extract track ID from URL
            track_id = self._extract_id_from_url(track_url)

            # Queue the download task - runs in worker where SpotifyClient is initialized
            await sync_to_async(download_single_track.delay)(track_id)

            if track_name:
                message = f"Started downloading track: {track_name}"
            else:
                message = f"Started downloading track (ID: {track_id})"

            return MutationResult(success=True, message=message)
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
