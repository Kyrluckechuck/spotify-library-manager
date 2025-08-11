import re
from typing import Optional, Tuple


def validate_spotify_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that the URL is a valid Spotify URL.

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not url:
        return False, "URL cannot be empty"

    # Use the same regex pattern as the original validator
    pattern = r"^(https:\/\/open.spotify.com\/|spotify:)([a-zA-Z0-9]+)(.*)"

    if not re.match(pattern, url):
        return (
            False,
            "Invalid Spotify URL. Please provide a valid Spotify URL (https://open.spotify.com/... or spotify:...)",
        )

    return True, None


def extract_spotify_id(url: str) -> Optional[str]:
    """
    Extract the Spotify ID from a valid Spotify URL.

    Returns:
        Optional[str]: The Spotify ID if found, None otherwise
    """
    # Pattern to extract the ID part - handle both web URLs and spotify: URIs
    web_pattern = r"(?:https:\/\/open\.spotify\.com\/)[a-zA-Z]+\/([a-zA-Z0-9]+)"
    uri_pattern = r"(?:spotify:)[a-zA-Z]+:([a-zA-Z0-9]+)"

    # Try web URL pattern first
    match = re.search(web_pattern, url)
    if match:
        return match.group(1)

    # Try spotify: URI pattern
    match = re.search(uri_pattern, url)
    if match:
        return match.group(1)

    return None


def is_spotify_playlist_url(url: str) -> bool:
    """
    Check if the URL is a Spotify playlist URL.
    """
    return "playlist" in url.lower()


def is_spotify_album_url(url: str) -> bool:
    """
    Check if the URL is a Spotify album URL.
    """
    return "album" in url.lower()


def is_spotify_track_url(url: str) -> bool:
    """
    Check if the URL is a Spotify track URL.
    """
    return "track" in url.lower()


def get_spotify_url_type(url: str) -> Optional[str]:
    """
    Get the type of Spotify URL (playlist, album, track, etc.).

    Returns:
        Optional[str]: The URL type if found, None otherwise
    """
    if not validate_spotify_url(url)[0]:
        return None

    url_lower = url.lower()

    if "playlist" in url_lower:
        return "playlist"
    if "album" in url_lower:
        return "album"
    if "track" in url_lower:
        return "track"
    if "artist" in url_lower:
        return "artist"

    return "unknown"
