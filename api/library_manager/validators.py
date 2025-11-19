"""
Validation utilities for Spotify Library Manager.

This module provides validation functions for Spotify identifiers and URIs.
"""

import re
from typing import Optional


def is_valid_spotify_id(spotify_id: str) -> bool:
    """
    Validate that a string is a valid Spotify ID.

    Spotify IDs are 22-character base62-encoded strings containing:
    - Uppercase letters (A-Z)
    - Lowercase letters (a-z)
    - Digits (0-9)

    Examples of valid Spotify IDs:
    - Artist: "4iV5W9uYEdYUVa79Axb7Rh"
    - Album: "7K3BhSpAxZBzniskgIPUYj"
    - Track: "6rqhFgbbKwnb9MLmUQDhG6"

    Args:
        spotify_id: The ID string to validate

    Returns:
        bool: True if valid Spotify ID, False otherwise

    Examples:
        >>> is_valid_spotify_id("4iV5W9uYEdYUVa79Axb7Rh")
        True
        >>> is_valid_spotify_id("85273dc1a556464e98d5faae420a5cbb")  # 32-char hex
        False
        >>> is_valid_spotify_id("invalid")
        False
    """
    if not spotify_id or not isinstance(spotify_id, str):
        return False

    # Spotify IDs are exactly 22 characters
    if len(spotify_id) != 22:
        return False

    # Must be base62 (alphanumeric only, no special chars)
    return bool(re.match(r"^[A-Za-z0-9]{22}$", spotify_id))


def extract_spotify_id_from_uri(uri: str) -> Optional[str]:
    """
    Extract Spotify ID from a Spotify URI.

    Supports various URI formats:
    - spotify:artist:4iV5W9uYEdYUVa79Axb7Rh
    - spotify:album:7K3BhSpAxZBzniskgIPUYj
    - spotify:track:6rqhFgbbKwnb9MLmUQDhG6
    - https://open.spotify.com/artist/4iV5W9uYEdYUVa79Axb7Rh
    - https://open.spotify.com/album/7K3BhSpAxZBzniskgIPUYj?si=...

    Args:
        uri: Spotify URI or URL string

    Returns:
        Optional[str]: Extracted 22-char Spotify ID, or None if invalid

    Examples:
        >>> extract_spotify_id_from_uri("spotify:artist:4iV5W9uYEdYUVa79Axb7Rh")
        "4iV5W9uYEdYUVa79Axb7Rh"
        >>> extract_spotify_id_from_uri("https://open.spotify.com/artist/4iV5W9uYEdYUVa79Axb7Rh")
        "4iV5W9uYEdYUVa79Axb7Rh"
        >>> extract_spotify_id_from_uri("invalid")
        None
    """
    if not uri or not isinstance(uri, str):
        return None

    # Try spotify: URI format
    uri_match = re.match(
        r"^spotify:(artist|album|track|playlist):([A-Za-z0-9]{22})$", uri
    )
    if uri_match:
        return uri_match.group(2)

    # Try HTTP(S) URL format
    url_match = re.match(
        r"^https?://open\.spotify\.com/(artist|album|track|playlist)/([A-Za-z0-9]{22})(?:\?.*)?$",
        uri,
    )
    if url_match:
        return url_match.group(2)

    # If it's already a bare ID, validate and return
    if is_valid_spotify_id(uri):
        return uri

    return None


def convert_hex_gid_to_spotify_id(hex_gid: str) -> str | None:
    """
    Convert hex-encoded Spotify GID to standard base62 Spotify ID.

    Legacy systems stored Spotify GIDs as 32-character hex strings.
    This function converts them to the standard 22-character base62 format
    that Spotify's API expects.

    Args:
        hex_gid: 32-character hex string (e.g., "85273dc1a556464e98d5faae420a5cbb")

    Returns:
        str | None: 22-character Spotify ID if conversion successful, None otherwise

    Examples:
        >>> convert_hex_gid_to_spotify_id("85273dc1a556464e98d5faae420a5cbb")
        "hFc9xqVWRk6Y1fquQgpc..."  # Base62 encoded
    """
    if not hex_gid or len(hex_gid) != 32:
        return None

    # Validate it's actually hex
    if not re.match(r"^[a-f0-9]{32}$", hex_gid.lower()):
        return None

    try:
        # Use the existing conversion function from downloader.utils
        from downloader.utils import gid_to_uri

        spotify_id = gid_to_uri(hex_gid)

        # Verify it produced a valid Spotify ID
        if is_valid_spotify_id(spotify_id):
            return spotify_id

        return None
    except (ValueError, TypeError, ImportError):
        return None


def normalize_spotify_gid(gid: str) -> str:
    """
    Normalize a Spotify GID to standard base62 format.

    Handles both legacy hex-encoded GIDs (32 chars) and modern base62 IDs (22 chars).
    Converts hex GIDs to base62 format automatically.

    Args:
        gid: Spotify GID in either hex (32 chars) or base62 (22 chars) format

    Returns:
        str: Normalized 22-character base62 Spotify ID

    Raises:
        ValueError: If GID cannot be normalized to valid format

    Examples:
        >>> normalize_spotify_gid("4iV5W9uYEdYUVa79Axb7Rh")  # Already base62
        "4iV5W9uYEdYUVa79Axb7Rh"

        >>> normalize_spotify_gid("85273dc1a556464e98d5faae420a5cbb")  # Hex GID
        "hFc9xqVWRk6Y1fquQgpc..."  # Converted to base62
    """
    if not gid:
        raise ValueError("Missing Spotify GID")

    # If already a valid Spotify ID, return as-is
    if is_valid_spotify_id(gid):
        return gid

    # If it's a 32-char hex GID, convert it
    if len(gid) == 32 and re.match(r"^[a-f0-9]{32}$", gid.lower()):
        converted = convert_hex_gid_to_spotify_id(gid)
        if converted:
            return converted
        raise ValueError(
            f"Failed to convert hex GID '{gid}' to Spotify ID. "
            f"The hex value may be malformed."
        )

    # Otherwise, it's invalid
    raise ValueError(
        f"Invalid Spotify GID: '{gid}'. "
        f"Expected either 22-char base62 ID or 32-char hex GID, "
        f"got {len(gid)}-character string."
    )


def validate_spotify_gid(gid: str, entity_type: str = "artist") -> None:
    """
    Validate a Spotify GID and raise descriptive error if invalid.

    This function should be called before using a GID in Spotify API calls
    to catch data quality issues early.

    DEPRECATED: Use normalize_spotify_gid() instead for automatic conversion.

    Args:
        gid: The GID to validate
        entity_type: Type of entity (for error message context)

    Raises:
        ValueError: If GID is invalid with detailed error message

    Examples:
        >>> validate_spotify_gid("4iV5W9uYEdYUVa79Axb7Rh", "artist")
        # No error - valid

        >>> validate_spotify_gid("85273dc1a556464e98d5faae420a5cbb", "artist")
        ValueError: Legacy hex-encoded GID detected...
    """
    if not gid:
        raise ValueError(f"Missing Spotify {entity_type} GID")

    if not is_valid_spotify_id(gid):
        error_msg = (
            f"Invalid Spotify {entity_type} GID: '{gid}'. "
            f"Expected 22-character base62 ID, got {len(gid)}-character string. "
        )

        # Provide helpful context for common issues
        if len(gid) == 32 and re.match(r"^[a-f0-9]{32}$", gid.lower()):
            error_msg += (
                "This appears to be a legacy hex-encoded GID. "
                "Use normalize_spotify_gid() to convert it to base62 format. "
                f"Converted value would be: {convert_hex_gid_to_spotify_id(gid)}"
            )
        elif len(gid) < 22:
            error_msg += "GID is too short to be a valid Spotify ID."
        elif len(gid) > 22:
            error_msg += "GID is too long to be a valid Spotify ID."
        else:
            error_msg += "GID contains invalid characters (must be alphanumeric only)."

        raise ValueError(error_msg)
