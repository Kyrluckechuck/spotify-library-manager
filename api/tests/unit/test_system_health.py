"""Unit tests for system health service."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock

from src.services.system_health import AuthenticationStatus, SystemHealthService


class TestSystemHealthService:
    """Tests for SystemHealthService."""

    def test_check_authentication_status_missing_cookies(self):
        """Test authentication status when cookies file is missing."""
        mock_config = MagicMock()
        mock_config.cookies_location = "/nonexistent/cookies.txt"

        result = SystemHealthService.check_authentication_status(mock_config)

        assert isinstance(result, AuthenticationStatus)
        assert not result.cookies_valid
        assert result.cookies_error_type == "missing"
        assert "not found" in result.cookies_error_message.lower()
        assert result.cookies_expire_in_days is None

    def test_check_authentication_status_malformed_cookies(self):
        """Test authentication status with malformed cookies."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write(".youtube.com\tTRUE\t/\tFALSE\t1770778578\n")  # Wrong field count
            temp_path = Path(f.name)

        try:
            mock_config = MagicMock()
            mock_config.cookies_location = str(temp_path)

            result = SystemHealthService.check_authentication_status(mock_config)

            assert not result.cookies_valid
            assert result.cookies_error_type == "malformed"
            assert result.cookies_error_message is not None
        finally:
            temp_path.unlink()

    def test_check_authentication_status_expired_cookies(self):
        """Test authentication status with expired cookies."""
        past_timestamp = int((datetime.now() - timedelta(days=30)).timestamp())

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write(
                f".youtube.com\tTRUE\t/\tFALSE\t{past_timestamp}\ttest_cookie\ttest_value\n"
            )
            temp_path = Path(f.name)

        try:
            mock_config = MagicMock()
            mock_config.cookies_location = str(temp_path)

            result = SystemHealthService.check_authentication_status(mock_config)

            assert not result.cookies_valid
            assert result.cookies_error_type == "expired"
            assert "expired" in result.cookies_error_message.lower()
            assert result.cookies_expire_in_days is not None
            assert result.cookies_expire_in_days < 0
        finally:
            temp_path.unlink()

    def test_check_authentication_status_valid_cookies(self):
        """Test authentication status with valid cookies."""
        future_timestamp = int((datetime.now() + timedelta(days=90)).timestamp())

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write(
                f".youtube.com\tTRUE\t/\tTRUE\t{future_timestamp}\t__Secure-1PSID\ttest_value\n"
            )
            temp_path = Path(f.name)

        try:
            mock_config = MagicMock()
            mock_config.cookies_location = str(temp_path)

            result = SystemHealthService.check_authentication_status(mock_config)

            assert result.cookies_valid
            assert result.cookies_error_type is None
            assert result.cookies_error_message is None
            assert result.cookies_expire_in_days is not None
            assert 89 <= result.cookies_expire_in_days <= 91
        finally:
            temp_path.unlink()

    def test_check_authentication_status_no_config(self):
        """Test authentication status with default config."""
        # This will use the default config and try /config/cookies.txt
        result = SystemHealthService.check_authentication_status(None)

        assert isinstance(result, AuthenticationStatus)
        # Result will depend on whether /config/cookies.txt exists
        # Just verify structure is correct
        assert isinstance(result.cookies_valid, bool)
        assert isinstance(result.po_token_configured, bool)

    def test_is_download_capable_valid_cookies(self):
        """Test download capability with valid cookies."""
        future_timestamp = int((datetime.now() + timedelta(days=90)).timestamp())

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write(
                f".youtube.com\tTRUE\t/\tTRUE\t{future_timestamp}\t__Secure-1PSID\ttest_value\n"
            )
            temp_path = Path(f.name)

        try:
            mock_config = MagicMock()
            mock_config.cookies_location = str(temp_path)

            can_download, reason = SystemHealthService.is_download_capable(mock_config)

            assert can_download is True
            assert reason is None
        finally:
            temp_path.unlink()

    def test_is_download_capable_invalid_cookies(self):
        """Test download capability with invalid cookies."""
        mock_config = MagicMock()
        mock_config.cookies_location = "/nonexistent/cookies.txt"

        can_download, reason = SystemHealthService.is_download_capable(mock_config)

        assert can_download is False
        assert reason is not None
        assert "cookies" in reason.lower()

    def test_is_download_capable_expired_cookies(self):
        """Test download capability with expired cookies."""
        past_timestamp = int((datetime.now() - timedelta(days=30)).timestamp())

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write(
                f".youtube.com\tTRUE\t/\tFALSE\t{past_timestamp}\ttest_cookie\ttest_value\n"
            )
            temp_path = Path(f.name)

        try:
            mock_config = MagicMock()
            mock_config.cookies_location = str(temp_path)

            can_download, reason = SystemHealthService.is_download_capable(mock_config)

            assert can_download is False
            assert "expired" in reason.lower()
        finally:
            temp_path.unlink()

    def test_is_download_capable_malformed_cookies(self):
        """Test download capability with malformed cookies."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write(".youtube.com\tTRUE\t/\tFALSE\t1770778578\n")  # Wrong field count
            temp_path = Path(f.name)

        try:
            mock_config = MagicMock()
            mock_config.cookies_location = str(temp_path)

            can_download, reason = SystemHealthService.is_download_capable(mock_config)

            assert can_download is False
            assert "malformed" in reason.lower()
        finally:
            temp_path.unlink()
