"""
Cookie file validator for YouTube Music authentication.

Validates cookies.txt file format (Netscape format) and checks for expiration.
Used by yt-dlp/spotdl for downloading music from YouTube Music.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class CookieValidationResult:
    """Result of cookie validation."""

    valid: bool
    error_type: Optional[str] = None  # 'missing', 'malformed', 'expired'
    error_message: Optional[str] = None
    expires_at: Optional[datetime] = None
    days_until_expiry: Optional[int] = None


class CookieValidator:
    """Validates YouTube Music cookie files for yt-dlp/spotdl."""

    REQUIRED_DOMAINS = [".youtube.com", "music.youtube.com"]
    # Don't require specific cookie names as they can vary (SAPISID, __Secure-*, etc.)
    REQUIRED_COOKIE_NAMES: list[str] = []

    @staticmethod
    def validate_netscape_format(
        line: str, line_num: int
    ) -> tuple[bool, Optional[str]]:
        """
        Validate a single line of Netscape cookie format.

        Format: domain\tflag\tpath\tsecure\texpiration\tname\tvalue

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Skip comments and empty lines
        if line.startswith("#") or not line.strip():
            return True, None

        parts = line.split("\t")
        if len(parts) != 7:
            return (
                False,
                f"Line {line_num}: Expected 7 tab-separated fields, got {len(parts)}",
            )

        domain, flag, path, secure, expiration, name, value = parts

        # Validate expiration is numeric
        try:
            int(expiration)
        except ValueError:
            return (
                False,
                f"Line {line_num}: Expiration must be numeric timestamp, got '{expiration}'",
            )

        # Validate secure flag
        if secure not in ("TRUE", "FALSE"):
            return (
                False,
                f"Line {line_num}: Secure flag must be TRUE or FALSE, got '{secure}'",
            )

        # Validate domain starts with dot or is exact match
        if not domain.startswith(".") and not domain.startswith("#HttpOnly_"):
            return (
                False,
                f"Line {line_num}: Domain should start with '.' or '#HttpOnly_', got '{domain}'",
            )

        return True, None

    @classmethod
    def validate_file(cls, cookie_path: Path) -> CookieValidationResult:
        """
        Validate cookies.txt file format and check expiration.

        Args:
            cookie_path: Path to cookies.txt file

        Returns:
            CookieValidationResult with validation details
        """
        # Check if file exists
        if not cookie_path.exists():
            return CookieValidationResult(
                valid=False,
                error_type="missing",
                error_message=f"Cookie file not found: {cookie_path}",
            )

        # Read and validate file
        try:
            content = cookie_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return CookieValidationResult(
                valid=False,
                error_type="malformed",
                error_message="Cookie file is not valid UTF-8 text",
            )
        except Exception as e:
            return CookieValidationResult(
                valid=False,
                error_type="malformed",
                error_message=f"Failed to read cookie file: {e}",
            )

        # Validate format line by line
        lines = content.split("\n")
        found_cookies = {}
        min_expiry: Optional[datetime] = None

        for line_num, line in enumerate(lines, start=1):
            is_valid, error = cls.validate_netscape_format(line, line_num)
            if not is_valid:
                return CookieValidationResult(
                    valid=False,
                    error_type="malformed",
                    error_message=error,
                )

            # Track required cookies and expiration
            if line.strip() and not line.startswith("#"):
                parts = line.split("\t")
                if len(parts) == 7:
                    domain, _, _, _, expiration, name, _ = parts

                    # Track required cookie names
                    if name in cls.REQUIRED_COOKIE_NAMES:
                        found_cookies[name] = True

                    # Track earliest expiration for YouTube cookies
                    if any(yt_domain in domain for yt_domain in cls.REQUIRED_DOMAINS):
                        try:
                            exp_timestamp = int(expiration)
                            # Skip session cookies (expiration = 0)
                            if exp_timestamp == 0:
                                continue
                            exp_datetime = datetime.fromtimestamp(exp_timestamp)

                            if min_expiry is None or exp_datetime < min_expiry:
                                min_expiry = exp_datetime
                        except (ValueError, OSError):
                            pass  # Skip invalid timestamps

        # Check for required cookies
        missing_cookies = [
            name for name in cls.REQUIRED_COOKIE_NAMES if name not in found_cookies
        ]
        if missing_cookies:
            return CookieValidationResult(
                valid=False,
                error_type="malformed",
                error_message=f"Missing required cookies: {', '.join(missing_cookies)}",
            )

        # Check expiration
        if min_expiry:
            now = datetime.now()
            if min_expiry < now:
                days_expired = (now - min_expiry).days
                return CookieValidationResult(
                    valid=False,
                    error_type="expired",
                    error_message=f"Cookies expired {days_expired} day(s) ago",
                    expires_at=min_expiry,
                    days_until_expiry=-days_expired,
                )

            days_until_expiry = (min_expiry - now).days
            return CookieValidationResult(
                valid=True,
                expires_at=min_expiry,
                days_until_expiry=days_until_expiry,
            )

        # No expiration found, assume valid but warn
        return CookieValidationResult(
            valid=True,
            error_message="Warning: Could not determine cookie expiration",
        )
