"""
Spotify URL/URI existence validation service.

Validates that Spotify resources (tracks, albums, playlists, artists) actually
exist on Spotify before queueing download tasks.
"""

# pylint: disable=R0911  # allow many return statements for validation logic
# pylint: disable=R1705  # allow explicit elif after return for clarity

import logging
import re
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class SpotifyValidationResult:
    """Result of Spotify resource validation."""

    valid: bool
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    error_message: Optional[str] = None


def extract_spotify_id_and_type(url: str) -> tuple[Optional[str], Optional[str]]:
    """
    Extract Spotify ID and resource type from URL or URI.

    Returns:
        Tuple of (resource_type, resource_id) or (None, None) if invalid
    """
    url = url.strip()

    # Handle Spotify URIs: spotify:type:id
    if url.startswith("spotify:"):
        parts = url.split(":")
        if len(parts) >= 3:
            return parts[1], parts[2]
        return None, None

    # Handle web URLs: https://open.spotify.com/type/id
    match = re.search(r"open\.spotify\.com/([^/?]+)/([^/?]+)", url)
    if match:
        return match.group(1), match.group(2)

    return None, None


def validate_spotify_resource(url: str) -> SpotifyValidationResult:
    """
    Validate that a Spotify resource exists.

    This function checks the Spotify API to verify the resource exists.
    Falls back gracefully if SpotifyClient is not initialized.

    Args:
        url: Spotify URL or URI

    Returns:
        SpotifyValidationResult with validation status and resource info
    """
    resource_type, resource_id = extract_spotify_id_and_type(url)

    if not resource_type or not resource_id:
        return SpotifyValidationResult(
            valid=False,
            error_message="Invalid Spotify URL format",
        )

    # Validate resource type
    valid_types = {"track", "album", "playlist", "artist"}
    if resource_type not in valid_types:
        return SpotifyValidationResult(
            valid=False,
            resource_type=resource_type,
            resource_id=resource_id,
            error_message=f"Unsupported resource type: {resource_type}",
        )

    try:
        from spotdl.utils.spotify import SpotifyClient

        # Check if SpotifyClient is initialized (singleton pattern requires _instance access)
        if SpotifyClient._instance is None:  # pylint: disable=protected-access
            logger.debug(
                "SpotifyClient not initialized - skipping existence validation"
            )
            # Return valid=True to allow task to proceed
            # Worker will handle the actual validation
            return SpotifyValidationResult(
                valid=True,
                resource_type=resource_type,
                resource_id=resource_id,
                resource_name=None,
            )

        client = SpotifyClient()

        # Fetch resource based on type
        if resource_type == "track":
            data = client.track(resource_id)
            if data:
                return SpotifyValidationResult(
                    valid=True,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    resource_name=data.get("name"),
                )
            return SpotifyValidationResult(
                valid=False,
                resource_type=resource_type,
                resource_id=resource_id,
                error_message="Track not found on Spotify",
            )

        elif resource_type == "album":
            data = client.album(resource_id)
            if data:
                return SpotifyValidationResult(
                    valid=True,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    resource_name=data.get("name"),
                )
            return SpotifyValidationResult(
                valid=False,
                resource_type=resource_type,
                resource_id=resource_id,
                error_message="Album not found on Spotify",
            )

        elif resource_type == "playlist":
            data = client.playlist(resource_id)
            if data:
                return SpotifyValidationResult(
                    valid=True,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    resource_name=data.get("name"),
                )
            return SpotifyValidationResult(
                valid=False,
                resource_type=resource_type,
                resource_id=resource_id,
                error_message="Playlist not found on Spotify (may be private or deleted)",
            )

        elif resource_type == "artist":
            data = client.artist(resource_id)
            if data:
                return SpotifyValidationResult(
                    valid=True,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    resource_name=data.get("name"),
                )
            return SpotifyValidationResult(
                valid=False,
                resource_type=resource_type,
                resource_id=resource_id,
                error_message="Artist not found on Spotify",
            )

    except Exception as e:
        error_str = str(e).lower()

        # Handle specific Spotify API errors
        if "404" in error_str or "not found" in error_str:
            return SpotifyValidationResult(
                valid=False,
                resource_type=resource_type,
                resource_id=resource_id,
                error_message=f"{resource_type.capitalize()} not found on Spotify",
            )

        if "401" in error_str or "unauthorized" in error_str:
            logger.warning(f"Spotify auth error during validation: {e}")
            # Allow to proceed - worker may have fresher credentials
            return SpotifyValidationResult(
                valid=True,
                resource_type=resource_type,
                resource_id=resource_id,
            )

        logger.warning(f"Spotify validation error: {e}")
        # On unexpected errors, allow to proceed
        return SpotifyValidationResult(
            valid=True,
            resource_type=resource_type,
            resource_id=resource_id,
        )

    # Should not reach here
    return SpotifyValidationResult(
        valid=True,
        resource_type=resource_type,
        resource_id=resource_id,
    )


async def validate_spotify_resource_async(url: str) -> SpotifyValidationResult:
    """Async wrapper for validate_spotify_resource."""
    from asgiref.sync import sync_to_async

    return await sync_to_async(validate_spotify_resource)(url)
