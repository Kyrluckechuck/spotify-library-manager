"""
System health service for monitoring authentication and configuration status.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from downloader.cookie_validator import CookieValidationResult, CookieValidator
from lib.config_class import Config


@dataclass
class AuthenticationStatus:
    """Authentication status for Spotify."""

    cookies_valid: bool
    cookies_error_type: Optional[str] = None  # 'missing', 'malformed', 'expired'
    cookies_error_message: Optional[str] = None
    cookies_expire_in_days: Optional[int] = None
    po_token_configured: bool = False


class SystemHealthService:
    """Service for checking system health and configuration."""

    @staticmethod
    def check_authentication_status(
        config: Optional[Config] = None,
    ) -> AuthenticationStatus:
        """
        Check Spotify authentication status (cookies and po_token).

        Args:
            config: Optional Config instance. If None, creates new one.

        Returns:
            AuthenticationStatus with current auth state
        """
        if config is None:
            config = Config()

        # Check cookies
        cookie_result: CookieValidationResult
        if config.cookies_location:
            cookie_path = Path(config.cookies_location)
            cookie_result = CookieValidator.validate_file(cookie_path)
        else:
            cookie_result = CookieValidationResult(
                valid=False,
                error_type="missing",
                error_message="Cookie file path not configured",
            )

        # Check po_token
        po_token_configured = bool(config.po_token and len(config.po_token.strip()) > 0)

        return AuthenticationStatus(
            cookies_valid=cookie_result.valid,
            cookies_error_type=cookie_result.error_type,
            cookies_error_message=cookie_result.error_message,
            cookies_expire_in_days=cookie_result.days_until_expiry,
            po_token_configured=po_token_configured,
        )

    @staticmethod
    def is_download_capable(
        config: Optional[Config] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Check if system can perform downloads.

        Returns:
            Tuple of (can_download, reason_if_not)
        """
        status = SystemHealthService.check_authentication_status(config)

        if not status.cookies_valid:
            return (
                False,
                f"Cookies {status.cookies_error_type}: {status.cookies_error_message}",
            )

        return True, None
