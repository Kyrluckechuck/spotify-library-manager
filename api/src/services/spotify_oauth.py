"""
Spotify OAuth service for managing user authentication tokens.

Handles OAuth flow for accessing private playlists and user-specific data.
"""

import secrets
from datetime import timedelta
from typing import Any, Dict, Optional
from urllib.parse import urlencode

from django.conf import settings
from django.utils import timezone

import requests
from asgiref.sync import sync_to_async

from library_manager.models import SpotifyOAuthToken


class SpotifyOAuthService:
    """Service for handling Spotify OAuth authentication."""

    # OAuth scopes needed for private playlist access
    SCOPES = [
        "playlist-read-private",
        "playlist-read-collaborative",
        "user-library-read",
        "user-follow-read",
    ]

    @staticmethod
    def get_authorization_url(
        state: Optional[str] = None, redirect_uri: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Generate Spotify OAuth authorization URL.

        Args:
            state: Optional state parameter for CSRF protection.
                   If not provided, a random state will be generated.
            redirect_uri: Optional redirect URI. If not provided, uses the configured
                         default or constructs from settings.

        Returns:
            Tuple of (authorization_url, state)
        """
        if state is None:
            state = secrets.token_urlsafe(32)

        client_id = getattr(settings, "SPOTIPY_CLIENT_ID", "")

        # Use provided redirect_uri, or fall back to configured value
        if redirect_uri is None:
            redirect_uri = getattr(
                settings,
                "spotify_redirect_uri",
                "http://127.0.0.1:5000/auth/spotify/callback",
            )

        params = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": " ".join(SpotifyOAuthService.SCOPES),
            "state": state,
            "show_dialog": "false",  # Don't force re-approval
        }

        auth_url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
        return auth_url, state

    @staticmethod
    def exchange_code_for_tokens(
        code: str, redirect_uri: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens.

        Args:
            code: Authorization code from Spotify OAuth callback
            redirect_uri: Optional redirect URI. Must match the one used in authorization.
                         If not provided, uses the configured default.

        Returns:
            Dict with token information

        Raises:
            requests.HTTPError: If token exchange fails
        """
        client_id = getattr(settings, "SPOTIPY_CLIENT_ID", "")
        client_secret = getattr(settings, "SPOTIPY_CLIENT_SECRET", "")

        if redirect_uri is None:
            redirect_uri = getattr(
                settings,
                "spotify_redirect_uri",
                "http://127.0.0.1:5000/auth/spotify/callback",
            )

        response = requests.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
            },
            auth=(client_id, client_secret),
            timeout=10,
        )

        response.raise_for_status()
        return response.json()

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an expired access token.

        Args:
            refresh_token: Refresh token from previous authorization

        Returns:
            Dict with new token information

        Raises:
            requests.HTTPError: If token refresh fails
        """
        client_id = getattr(settings, "SPOTIPY_CLIENT_ID", "")
        client_secret = getattr(settings, "SPOTIPY_CLIENT_SECRET", "")

        response = requests.post(
            "https://accounts.spotify.com/api/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            auth=(client_id, client_secret),
            timeout=10,
        )

        response.raise_for_status()
        return response.json()

    @staticmethod
    def save_tokens(token_data: Dict[str, Any]) -> SpotifyOAuthToken:
        """
        Save OAuth tokens to database (singleton pattern).

        Args:
            token_data: Token data from Spotify OAuth response

        Returns:
            SpotifyOAuthToken instance
        """
        expires_in = token_data.get("expires_in", 3600)
        expires_at = timezone.now() + timedelta(seconds=expires_in)

        # Use get_or_create to ensure singleton
        token, created = SpotifyOAuthToken.objects.get_or_create(
            id=1,  # Singleton - always use ID 1
            defaults={
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token", ""),
                "token_type": token_data.get("token_type", "Bearer"),
                "expires_at": expires_at,
                "scope": token_data.get("scope", " ".join(SpotifyOAuthService.SCOPES)),
            },
        )

        if not created:
            # Update existing token
            token.access_token = token_data["access_token"]
            if "refresh_token" in token_data:
                token.refresh_token = token_data["refresh_token"]
            token.token_type = token_data.get("token_type", "Bearer")
            token.expires_at = expires_at
            token.scope = token_data.get("scope", " ".join(SpotifyOAuthService.SCOPES))
            token.save()

        return token

    @staticmethod
    async def get_valid_token() -> Optional[SpotifyOAuthToken]:
        """
        Get a valid access token, refreshing if necessary.

        Returns:
            SpotifyOAuthToken with valid access token, or None if not authenticated
        """

        def _get_token():
            try:
                token = SpotifyOAuthToken.objects.get(id=1)
                return token
            except SpotifyOAuthToken.DoesNotExist:
                return None

        token = await sync_to_async(_get_token)()

        if token is None:
            return None

        # Check if token needs refresh
        if token.is_expired():
            # Refresh the token
            try:
                new_token_data = SpotifyOAuthService.refresh_access_token(
                    token.refresh_token
                )
                token = await sync_to_async(SpotifyOAuthService.save_tokens)(
                    new_token_data
                )
            except requests.HTTPError:
                # Refresh failed - token is invalid
                return None

        return token

    @staticmethod
    async def is_authenticated() -> bool:
        """Check if user has authenticated with Spotify OAuth."""
        token = await SpotifyOAuthService.get_valid_token()
        return token is not None

    @staticmethod
    def revoke_tokens() -> None:
        """Revoke and delete stored OAuth tokens."""
        SpotifyOAuthToken.objects.filter(id=1).delete()
        return None
