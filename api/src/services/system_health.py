"""
System health service for monitoring authentication and configuration status.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from downloader.cookie_validator import CookieValidationResult, CookieValidator
from downloader.premium_detector import PremiumDetector
from lib.config_class import Config


@dataclass
class AuthenticationStatus:  # pylint: disable=too-many-instance-attributes
    """Authentication status for YouTube Music Premium and Spotify access."""

    # YouTube Music authentication (for high-quality audio downloads)
    cookies_valid: bool
    cookies_error_type: Optional[str] = None  # 'missing', 'malformed', 'expired'
    cookies_error_message: Optional[str] = None
    cookies_expire_in_days: Optional[int] = None
    po_token_configured: bool = False
    po_token_valid: bool = False
    po_token_error_message: Optional[str] = None

    # Spotify authentication mode (for playlist access)
    spotify_user_auth_enabled: bool = False
    spotify_auth_mode: str = (
        "public"  # 'public' (public playlists only) or 'user-authenticated' (includes private)
    )

    # Spotify OAuth token status (when using user-authenticated mode)
    spotify_token_valid: bool = True
    spotify_token_expired: bool = False
    spotify_token_expires_in_hours: Optional[int] = None
    spotify_token_error_message: Optional[str] = None


class SystemHealthService:
    """Service for checking system health and configuration."""

    # Shared PremiumDetector instance for caching validation results
    _detector_cache: Dict[str, PremiumDetector] = {}

    @staticmethod
    def _check_spotify_oauth_token_exists() -> bool:
        """
        Sync helper to check if Spotify OAuth token exists in database.

        This method is separated so it can be properly called from async contexts.
        """
        import logging

        from library_manager.models import SpotifyOAuthToken

        logger = logging.getLogger(__name__)

        try:
            token = SpotifyOAuthToken.objects.get(id=1)
            logger.info(
                f"OAuth token check: FOUND token with access_token length {len(token.access_token)}"
            )
            return True
        except SpotifyOAuthToken.DoesNotExist:
            logger.info("OAuth token check: Token does NOT exist")
            return False
        except Exception as e:
            # Handle any unexpected errors (e.g., database connection issues)
            logger.error(
                f"OAuth token check: Exception occurred: {type(e).__name__}: {e}"
            )
            return False

    @staticmethod
    def _check_spotify_oauth_token_status() -> Dict[str, Any]:
        """
        Check Spotify OAuth token validity and expiration status.

        If the token is expired or expiring soon, this will attempt to refresh it
        automatically using the refresh token.

        Returns:
            Dict with token status information:
            - valid: bool - Whether token exists and is not expired
            - expired: bool - Whether token is expired
            - expires_in_hours: Optional[int] - Hours until expiration
            - error_message: Optional[str] - Error message if any
        """
        import logging

        from django.utils import timezone

        from library_manager.models import SpotifyOAuthToken

        logger = logging.getLogger(__name__)

        try:
            token = SpotifyOAuthToken.objects.get(id=1)

            # Check if token needs refresh (expired or expiring within 5 minutes)
            if token.is_expired():
                # Attempt to refresh the token proactively
                logger.info(
                    "Spotify OAuth token expired or expiring soon, attempting refresh"
                )
                try:
                    from src.services.spotify_oauth import SpotifyOAuthService

                    new_token_data = SpotifyOAuthService.refresh_access_token(
                        token.refresh_token
                    )
                    token = SpotifyOAuthService.save_tokens(new_token_data)
                    logger.info("Successfully refreshed Spotify OAuth token")
                except Exception as refresh_error:
                    logger.error(
                        f"Failed to refresh Spotify OAuth token: {refresh_error}"
                    )
                    return {
                        "valid": False,
                        "expired": True,
                        "expires_in_hours": None,
                        "error_message": "Spotify OAuth token has expired and refresh failed. Please re-authenticate.",
                    }

            # Token is now valid (either it was valid, or we just refreshed it)
            now = timezone.now()

            # Calculate hours until expiration
            time_until_expiry = token.expires_at - now
            hours_until_expiry = int(time_until_expiry.total_seconds() / 3600)

            return {
                "valid": True,
                "expired": False,
                "expires_in_hours": hours_until_expiry,
                "error_message": None,
            }

        except SpotifyOAuthToken.DoesNotExist:
            # No token stored - not an error if not using OAuth
            return {
                "valid": True,  # Consider valid if not using OAuth
                "expired": False,
                "expires_in_hours": None,
                "error_message": None,
            }
        except Exception as e:
            logger.error(f"Error checking Spotify OAuth token status: {e}")
            return {
                "valid": False,
                "expired": False,
                "expires_in_hours": None,
                "error_message": f"Error checking token: {str(e)}",
            }

    @staticmethod
    def _get_detector(config: Config) -> PremiumDetector:
        """
        Get or create a cached PremiumDetector instance.

        Uses cookies_location + po_token as cache key to reuse detector instances
        and preserve validation cache across multiple health checks.
        """
        cache_key = f"{config.youtube_cookies_location}:{config.po_token}"

        if cache_key not in SystemHealthService._detector_cache:
            SystemHealthService._detector_cache[cache_key] = PremiumDetector(
                cookies_file=(
                    str(config.youtube_cookies_location)
                    if config.youtube_cookies_location
                    else None
                ),
                po_token=config.po_token,
            )

        return SystemHealthService._detector_cache[cache_key]

    @staticmethod
    def check_authentication_status(
        config: Optional[Config] = None,
    ) -> AuthenticationStatus:
        """
        Check YouTube Music Premium authentication status (cookies and po_token).

        This system requires BOTH valid cookies AND a valid PO token for premium downloads.

        Args:
            config: Optional Config instance. If None, creates new one.

        Returns:
            AuthenticationStatus with current auth state
        """
        if config is None:
            config = Config()

        # Check YouTube cookies
        cookie_result: CookieValidationResult
        if config.youtube_cookies_location:
            cookie_path = Path(config.youtube_cookies_location)
            cookie_result = CookieValidator.validate_file(cookie_path)
        else:
            cookie_result = CookieValidationResult(
                valid=False,
                error_type="missing",
                error_message="Cookie file path not configured",
            )

        # Check po_token - REQUIRED for premium
        # First do format validation
        format_result = CookieValidator.validate_po_token(config.po_token)
        po_token_configured = bool(config.po_token and len(config.po_token.strip()) > 0)

        # If format is valid AND cookies are valid, do live validation against YouTube API
        # (PO token validation requires valid cookies to work)
        if format_result.valid and cookie_result.valid:
            # Use cached detector instance to preserve validation cache
            detector = SystemHealthService._get_detector(config)
            po_token_result = detector.validate_po_token_live()
        else:
            # Format invalid OR cookies invalid - can't do live validation
            # Convert format result to match live validation result structure
            from downloader.premium_detector import (
                PoTokenValidationResult as LivePoTokenValidationResult,
            )

            if not format_result.valid:
                # Format validation failed
                error_msg = format_result.error_message
            else:
                # Cookies are invalid, can't test PO token
                error_msg = (
                    "Cannot validate PO token - cookies are invalid. Fix cookies first."
                )

            po_token_result = LivePoTokenValidationResult(
                valid=False,
                error_message=error_msg,
                can_authenticate=False,
            )

        # Check Spotify authentication mode and OAuth connection status
        import logging

        logger = logging.getLogger(__name__)

        spotify_user_auth = config.spotify_user_auth_enabled
        # Check if OAuth tokens are actually stored
        has_oauth_token = SystemHealthService._check_spotify_oauth_token_exists()
        spotify_mode = "user-authenticated" if has_oauth_token else "public"

        logger.info(
            f"Spotify auth check: has_oauth_token={has_oauth_token}, spotify_mode={spotify_mode}"
        )

        # Check Spotify OAuth token status (expiration, validity)
        spotify_token_status = SystemHealthService._check_spotify_oauth_token_status()

        return AuthenticationStatus(
            cookies_valid=cookie_result.valid,
            cookies_error_type=cookie_result.error_type,
            cookies_error_message=cookie_result.error_message,
            cookies_expire_in_days=cookie_result.days_until_expiry,
            po_token_configured=po_token_configured,
            po_token_valid=po_token_result.valid,
            po_token_error_message=po_token_result.error_message,
            spotify_user_auth_enabled=spotify_user_auth,
            spotify_auth_mode=spotify_mode,
            spotify_token_valid=spotify_token_status["valid"],
            spotify_token_expired=spotify_token_status["expired"],
            spotify_token_expires_in_hours=spotify_token_status["expires_in_hours"],
            spotify_token_error_message=spotify_token_status["error_message"],
        )

    @staticmethod
    def is_download_capable(
        config: Optional[Config] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Check if system can perform premium downloads.

        Requires BOTH valid cookies AND valid PO token for YouTube Music Premium.

        Returns:
            Tuple of (can_download, reason_if_not)
        """
        status = SystemHealthService.check_authentication_status(config)

        # Check cookies first
        if not status.cookies_valid:
            return (
                False,
                f"Cookies {status.cookies_error_type}: {status.cookies_error_message}",
            )

        # Check PO token - REQUIRED for premium
        if not status.po_token_valid:
            return (
                False,
                f"PO Token invalid: {status.po_token_error_message}. This system requires YouTube Music Premium authentication.",
            )

        return True, None
