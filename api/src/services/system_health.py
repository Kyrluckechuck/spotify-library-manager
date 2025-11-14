"""
System health service for monitoring authentication and configuration status.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from downloader.cookie_validator import CookieValidationResult, CookieValidator
from downloader.premium_detector import PremiumDetector
from lib.config_class import Config


@dataclass
class AuthenticationStatus:
    """Authentication status for YouTube Music Premium."""

    cookies_valid: bool
    cookies_error_type: Optional[str] = None  # 'missing', 'malformed', 'expired'
    cookies_error_message: Optional[str] = None
    cookies_expire_in_days: Optional[int] = None
    po_token_configured: bool = False
    po_token_valid: bool = False
    po_token_error_message: Optional[str] = None


class SystemHealthService:
    """Service for checking system health and configuration."""

    # Shared PremiumDetector instance for caching validation results
    _detector_cache: Dict[str, PremiumDetector] = {}

    @staticmethod
    def _get_detector(config: Config) -> PremiumDetector:
        """
        Get or create a cached PremiumDetector instance.

        Uses cookies_location + po_token as cache key to reuse detector instances
        and preserve validation cache across multiple health checks.
        """
        cache_key = f"{config.cookies_location}:{config.po_token}"

        if cache_key not in SystemHealthService._detector_cache:
            SystemHealthService._detector_cache[cache_key] = PremiumDetector(
                cookies_file=(
                    str(config.cookies_location) if config.cookies_location else None
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

        return AuthenticationStatus(
            cookies_valid=cookie_result.valid,
            cookies_error_type=cookie_result.error_type,
            cookies_error_message=cookie_result.error_message,
            cookies_expire_in_days=cookie_result.days_until_expiry,
            po_token_configured=po_token_configured,
            po_token_valid=po_token_result.valid,
            po_token_error_message=po_token_result.error_message,
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
