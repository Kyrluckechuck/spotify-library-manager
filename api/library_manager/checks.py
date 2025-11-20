"""
Django system checks for application health.

These checks run at startup and with 'python manage.py check'.
"""

import os
from pathlib import Path
from typing import Any, List

from django.conf import settings
from django.core.checks import CheckMessage, Error, Warning, register

from downloader.cookie_validator import CookieValidator


@register()
def check_cookie_file(app_configs: Any, **kwargs: Any) -> List[CheckMessage]:
    """
    Check that youtube_music_cookies.txt file exists and is valid.

    This is critical for YouTube Music downloads to work (via yt-dlp/spotdl).
    In CI/test environments, missing cookies are downgraded to warnings.
    """
    errors: List[CheckMessage] = []

    # Detect CI/test environments where cookies aren't available
    is_ci = (
        os.environ.get("CI") == "true"
        or os.environ.get("GITHUB_ACTIONS") == "true"
        or os.environ.get("GITLAB_CI") == "true"
        or "test" in os.environ.get("DJANGO_SETTINGS_MODULE", "").lower()
    )

    # Get YouTube cookie path from settings
    cookie_path = getattr(settings, "COOKIE_FILE_PATH", None)
    if not cookie_path:
        # Try youtube_cookies_location (new default)
        cookie_path = Path(
            getattr(
                settings,
                "youtube_cookies_location",
                "/config/youtube_music_cookies.txt",
            )
        )

    cookie_path = Path(cookie_path)

    # Validate cookies
    result = CookieValidator.validate_file(cookie_path)

    if not result.valid:
        if result.error_type == "missing":
            # In CI/test, downgrade to warning since downloads won't work anyway
            check_class = Warning if is_ci else Error
            check_id = "spotify.W002" if is_ci else "spotify.E001"
            errors.append(
                check_class(
                    "YouTube Music cookies file not found",
                    hint=f"Create youtube_youtube_music_cookies.txt at {cookie_path}. Downloads will not work without valid cookies.",
                    obj="cookies",
                    id=check_id,
                )
            )
        elif result.error_type == "malformed":
            # In CI/test, downgrade to warning
            check_class = Warning if is_ci else Error
            check_id = "spotify.W003" if is_ci else "spotify.E002"
            errors.append(
                check_class(
                    f"YouTube Music cookies file is malformed: {result.error_message}",
                    hint="Export cookies in Netscape format from YouTube Music in your browser",
                    obj="cookies",
                    id=check_id,
                )
            )
        elif result.error_type == "expired":
            # In CI/test, downgrade to warning
            check_class = Warning if is_ci else Error
            check_id = "spotify.W004" if is_ci else "spotify.E003"
            errors.append(
                check_class(
                    f"YouTube Music cookies have expired: {result.error_message}",
                    hint="Re-export cookies from YouTube Music in your browser",
                    obj="cookies",
                    id=check_id,
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
