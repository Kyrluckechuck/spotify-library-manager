"""
Django system checks for application health.

These checks run at startup and with 'python manage.py check'.
"""

from pathlib import Path

from django.conf import settings
from django.core.checks import Error, Warning, register

from downloader.cookie_validator import CookieValidator


@register()
def check_cookie_file(app_configs, **kwargs):
    """
    Check that cookies.txt file exists and is valid.

    This is critical for YouTube Music downloads to work (via yt-dlp/spotdl).
    """
    errors = []

    # Get cookie path from settings
    cookie_path = getattr(settings, "COOKIE_FILE_PATH", None)
    if not cookie_path:
        # Try default location
        cookie_path = Path("/config/cookies.txt")

    cookie_path = Path(cookie_path)

    # Validate cookies
    result = CookieValidator.validate_file(cookie_path)

    if not result.valid:
        if result.error_type == "missing":
            errors.append(
                Error(
                    "YouTube Music cookies file not found",
                    hint=f"Create cookies.txt at {cookie_path}",
                    obj="cookies",
                    id="spotify.E001",
                )
            )
        elif result.error_type == "malformed":
            errors.append(
                Error(
                    f"YouTube Music cookies file is malformed: {result.error_message}",
                    hint="Export cookies in Netscape format from YouTube Music in your browser",
                    obj="cookies",
                    id="spotify.E002",
                )
            )
        elif result.error_type == "expired":
            errors.append(
                Error(
                    f"YouTube Music cookies have expired: {result.error_message}",
                    hint="Re-export cookies from YouTube Music in your browser",
                    obj="cookies",
                    id="spotify.E003",
                )
            )
    elif result.days_until_expiry is not None and result.days_until_expiry < 7:
        errors.append(
            Warning(
                f"YouTube Music cookies will expire in {result.days_until_expiry} day(s)",
                hint="Consider re-exporting cookies soon",
                obj="cookies",
                id="spotify.W001",
            )
        )

    return errors
