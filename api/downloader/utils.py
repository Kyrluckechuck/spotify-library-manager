from datetime import datetime
from urllib.parse import urljoin, urlparse

import base62
from lib.config_class import Config


def convert_date_string_to_datetime(string: str) -> datetime:
    added_at: str = string
    # Convert from Zulu UTC to datetime UTC
    added_at = added_at.replace("Z", "+00:00")
    return datetime.fromisoformat(added_at)


def update_process_info(config: Config, progress: int) -> None:
    if config.process_info is None:
        return
    config.process_info.total_progress = progress
    config.process_info.update(n=0)


def uri_to_gid(uri: str) -> str:
    return hex(base62.decode(uri, base62.CHARSET_INVERTED))[2:].zfill(32)


def gid_to_uri(gid: str) -> str:
    result = base62.encode(int(gid, 16), charset=base62.CHARSET_INVERTED)
    return str(result).zfill(22)


def sanitize_and_strip_url(raw_url: str) -> str:
    raw_url = raw_url.strip()

    # Strip "personalized" tokens spotify auto-inserts into http URLs (Not applicable to URIs)
    if raw_url.startswith("http"):
        raw_url = urljoin(raw_url, urlparse(raw_url).path)

    return raw_url


def normalize_spotify_url(url: str) -> str:
    """Convert various Spotify URL formats to a standard URI format, stripping tracking parameters.

    This ensures consistent URL format for database lookups and storage.

    Args:
        url: Spotify URL in any format (HTTP with/without params, or URI)

    Returns:
        Normalized Spotify URI (e.g., "spotify:playlist:4tFwfZE3huEB7e8LRnKwmY")

    Examples:
        >>> normalize_spotify_url("https://open.spotify.com/playlist/ABC?si=123")
        "spotify:playlist:ABC"
        >>> normalize_spotify_url("spotify:playlist:ABC")
        "spotify:playlist:ABC"
    """
    import re

    # Handle spotify: URIs (already normalized)
    if url.startswith("spotify:"):
        return url

    # Handle web URLs - extract content type and ID, ignoring parameters
    if "open.spotify.com" in url:
        match = re.search(r"open\.spotify\.com/([^/?]+)/([^/?]+)", url)
        if match:
            content_type, content_id = match.groups()
            return f"spotify:{content_type}:{content_id}"

    return url
