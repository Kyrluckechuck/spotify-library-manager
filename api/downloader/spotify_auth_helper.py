"""
Helper module for integrating Spotify OAuth tokens with SpotDL.

Provides functionality to check for stored OAuth tokens and use them
with spotipy for accessing private playlists.
"""

import logging
from typing import Optional

from library_manager.models import SpotifyOAuthToken

logger = logging.getLogger(__name__)


def get_spotify_oauth_credentials() -> Optional[dict]:
    """
    Get Spotify OAuth credentials from database if available.

    Returns:
        Dict with OAuth credentials, or None if not authenticated
    """
    try:
        # Import here to avoid issues during module initialization
        from django.core.exceptions import SynchronousOnlyOperation

        try:
            token = SpotifyOAuthToken.objects.get(id=1)

            # Check if token is expired
            if token.is_expired():
                logger.warning("Spotify OAuth token is expired - needs refresh")
                # Token will be auto-refreshed when used by SpotifyOAuthService
                return None

            return {
                "access_token": token.access_token,
                "refresh_token": token.refresh_token,
                "token_type": token.token_type,
                "expires_at": token.expires_at.timestamp(),
            }

        except SynchronousOnlyOperation:
            # Called from async context or during app initialization
            # Return None to use client credentials instead
            logger.debug(
                "Cannot check OAuth tokens during async/init context - using client credentials"
            )
            return None

    except SpotifyOAuthToken.DoesNotExist:
        logger.debug("No Spotify OAuth tokens found - using client credentials")
        return None
    except Exception as e:
        logger.warning(f"Error checking OAuth tokens: {e} - using client credentials")
        return None
