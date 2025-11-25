# mypy: disable-error-code=attr-defined
"""
Spotify Search Service - Searches Spotify's API for artists, albums, tracks, and playlists.

This is distinct from the local database search (which filters already-imported data).
This service queries Spotify directly to find new content to track/import.
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from asgiref.sync import sync_to_async
from spotipy import Spotify


@dataclass
class SpotifySearchArtist:  # pylint: disable=too-many-instance-attributes
    """Artist result from Spotify search."""

    id: str
    name: str
    spotify_uri: str
    image_url: Optional[str]
    follower_count: int
    genres: List[str]
    # Whether this artist is already in our local database
    in_library: bool = False
    local_id: Optional[int] = None
    # Whether this artist is being tracked (only set if in_library is True)
    is_tracked: bool = False


@dataclass
class SpotifySearchAlbum:  # pylint: disable=too-many-instance-attributes
    """Album result from Spotify search."""

    id: str
    name: str
    spotify_uri: str
    image_url: Optional[str]
    artist_name: str
    artist_id: str
    release_date: Optional[str]
    album_type: str
    total_tracks: int
    # Whether this album is already in our local database
    in_library: bool = False
    local_id: Optional[int] = None


@dataclass
class SpotifySearchTrack:  # pylint: disable=too-many-instance-attributes
    """Track result from Spotify search."""

    id: str
    name: str
    spotify_uri: str
    artist_name: str
    artist_id: str
    album_name: str
    album_id: str
    duration_ms: int
    # Whether this track is already in our local database
    in_library: bool = False
    local_id: Optional[int] = None


@dataclass
class SpotifySearchPlaylist:  # pylint: disable=too-many-instance-attributes
    """Playlist result from Spotify search."""

    id: str
    name: str
    spotify_uri: str
    image_url: Optional[str]
    owner_name: str
    track_count: int
    description: Optional[str]
    # Whether this playlist is already tracked
    in_library: bool = False
    local_id: Optional[int] = None


@dataclass
class SpotifySearchResults:
    """Combined search results from Spotify."""

    artists: List[SpotifySearchArtist]
    albums: List[SpotifySearchAlbum]
    tracks: List[SpotifySearchTrack]
    playlists: List[SpotifySearchPlaylist]


class SpotifySearchService:
    """Service for searching Spotify's catalog."""

    def _get_spotify_client(self) -> Spotify:
        """Get an authenticated Spotify client."""
        from downloader.spotipy_tasks import SpotifyClient

        return SpotifyClient().sp

    async def search(
        self,
        query: str,
        types: Optional[List[str]] = None,
        limit: int = 10,
    ) -> SpotifySearchResults:
        """
        Search Spotify for artists, albums, tracks, and playlists.

        Args:
            query: The search query string
            types: List of types to search for ('artist', 'album', 'track', 'playlist')
                   If None, searches all types
            limit: Maximum results per type (default 10, max 50)

        Returns:
            SpotifySearchResults with results for each requested type
        """
        if not types:
            types = ["artist", "album", "track", "playlist"]

        # Clamp limit to Spotify's max of 50
        limit = min(limit, 50)

        # Build the type string for Spotify API
        type_str = ",".join(types)

        # Execute the search
        results = await sync_to_async(self._execute_search)(query, type_str, limit)

        # Process results and check against local database
        return await self._process_results(results, types)

    def _execute_search(self, query: str, type_str: str, limit: int) -> Dict[str, Any]:
        """Execute the actual Spotify search (sync)."""
        sp = self._get_spotify_client()
        result: Dict[str, Any] = sp.search(q=query, type=type_str, limit=limit)
        return result

    async def _process_results(
        self, results: dict, types: List[str]
    ) -> SpotifySearchResults:
        """Process Spotify API results and enrich with local database info."""
        artists: List[SpotifySearchArtist] = []
        albums: List[SpotifySearchAlbum] = []
        tracks: List[SpotifySearchTrack] = []
        playlists: List[SpotifySearchPlaylist] = []

        # Process artists
        if "artist" in types and "artists" in results:
            artists = await self._process_artists(results["artists"].get("items", []))

        # Process albums
        if "album" in types and "albums" in results:
            albums = await self._process_albums(results["albums"].get("items", []))

        # Process tracks
        if "track" in types and "tracks" in results:
            tracks = await self._process_tracks(results["tracks"].get("items", []))

        # Process playlists
        if "playlist" in types and "playlists" in results:
            playlists = await self._process_playlists(
                results["playlists"].get("items", [])
            )

        return SpotifySearchResults(
            artists=artists,
            albums=albums,
            tracks=tracks,
            playlists=playlists,
        )

    async def _process_artists(self, items: List[dict]) -> List[SpotifySearchArtist]:
        """Process artist results and check if they exist locally."""
        from library_manager.models import Artist as DjangoArtist

        processed = []
        for item in items:
            if not item:
                continue

            spotify_id = item.get("id", "")
            spotify_uri = item.get("uri", f"spotify:artist:{spotify_id}")

            # Get the best available image
            images = item.get("images", [])
            image_url = images[0]["url"] if images else None

            # Check if artist exists locally (by GID which is the Spotify ID)
            local_artist = await sync_to_async(
                lambda sid=spotify_id: DjangoArtist.objects.filter(gid=sid).first()
            )()

            processed.append(
                SpotifySearchArtist(
                    id=spotify_id,
                    name=item.get("name", "Unknown"),
                    spotify_uri=spotify_uri,
                    image_url=image_url,
                    follower_count=item.get("followers", {}).get("total", 0),
                    genres=item.get("genres", []),
                    in_library=local_artist is not None,
                    local_id=local_artist.id if local_artist else None,
                    is_tracked=local_artist.tracked if local_artist else False,
                )
            )

        return processed

    async def _process_albums(self, items: List[dict]) -> List[SpotifySearchAlbum]:
        """Process album results and check if they exist locally."""
        from library_manager.models import Album as DjangoAlbum

        processed = []
        for item in items:
            if not item:
                continue

            spotify_id = item.get("id", "")
            spotify_uri = item.get("uri", f"spotify:album:{spotify_id}")

            # Get artist info
            artists = item.get("artists", [])
            artist_name = artists[0]["name"] if artists else "Unknown"
            artist_id = artists[0]["id"] if artists else ""

            # Get the best available image
            images = item.get("images", [])
            image_url = images[0]["url"] if images else None

            # Check if album exists locally (by spotify_gid)
            local_album = await sync_to_async(
                lambda sid=spotify_id: DjangoAlbum.objects.filter(
                    spotify_gid=sid
                ).first()
            )()

            processed.append(
                SpotifySearchAlbum(
                    id=spotify_id,
                    name=item.get("name", "Unknown"),
                    spotify_uri=spotify_uri,
                    image_url=image_url,
                    artist_name=artist_name,
                    artist_id=artist_id,
                    release_date=item.get("release_date"),
                    album_type=item.get("album_type", "album"),
                    total_tracks=item.get("total_tracks", 0),
                    in_library=local_album is not None,
                    local_id=local_album.id if local_album else None,
                )
            )

        return processed

    async def _process_tracks(self, items: List[dict]) -> List[SpotifySearchTrack]:
        """Process track results and check if they exist locally."""
        from library_manager.models import Song as DjangoSong

        processed = []
        for item in items:
            if not item:
                continue

            spotify_id = item.get("id", "")
            spotify_uri = item.get("uri", f"spotify:track:{spotify_id}")

            # Get artist info
            artists = item.get("artists", [])
            artist_name = artists[0]["name"] if artists else "Unknown"
            artist_id = artists[0]["id"] if artists else ""

            # Get album info
            album = item.get("album", {})
            album_name = album.get("name", "Unknown")
            album_id = album.get("id", "")

            # Check if track exists locally (by gid)
            local_song = await sync_to_async(
                lambda sid=spotify_id: DjangoSong.objects.filter(gid=sid).first()
            )()

            processed.append(
                SpotifySearchTrack(
                    id=spotify_id,
                    name=item.get("name", "Unknown"),
                    spotify_uri=spotify_uri,
                    artist_name=artist_name,
                    artist_id=artist_id,
                    album_name=album_name,
                    album_id=album_id,
                    duration_ms=item.get("duration_ms", 0),
                    in_library=local_song is not None,
                    local_id=local_song.id if local_song else None,
                )
            )

        return processed

    async def _process_playlists(
        self, items: List[dict]
    ) -> List[SpotifySearchPlaylist]:
        """Process playlist results and check if they exist locally."""
        from library_manager.models import TrackedPlaylist

        processed = []
        for item in items:
            if not item:
                continue

            spotify_id = item.get("id", "")
            spotify_uri = item.get("uri", f"spotify:playlist:{spotify_id}")

            # Get the best available image
            images = item.get("images", [])
            image_url = images[0]["url"] if images else None

            # Get owner info
            owner = item.get("owner", {})
            owner_name = owner.get("display_name", "Unknown")

            # Check if playlist is tracked locally
            local_playlist = await sync_to_async(
                lambda sid=spotify_id: TrackedPlaylist.objects.filter(
                    url__contains=sid
                ).first()
            )()

            processed.append(
                SpotifySearchPlaylist(
                    id=spotify_id,
                    name=item.get("name", "Unknown"),
                    spotify_uri=spotify_uri,
                    image_url=image_url,
                    owner_name=owner_name,
                    track_count=item.get("tracks", {}).get("total", 0),
                    description=item.get("description"),
                    in_library=local_playlist is not None,
                    local_id=local_playlist.id if local_playlist else None,
                )
            )

        return processed
