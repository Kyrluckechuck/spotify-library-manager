"""Unit tests for cookie validator."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from downloader.cookie_validator import CookieValidator


class TestCookieValidator:
    """Tests for CookieValidator class."""

    def test_validate_missing_file(self):
        """Test validation of missing cookie file."""
        result = CookieValidator.validate_file(
            Path("/nonexistent/youtube_music_cookies.txt")
        )

        assert not result.valid
        assert result.error_type == "missing"
        assert "not found" in result.error_message.lower()

    def test_validate_malformed_file_invalid_utf8(self):
        """Test validation of file with invalid UTF-8."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".txt") as f:
            f.write(b"\x80\x81\x82")
            temp_path = Path(f.name)

        try:
            result = CookieValidator.validate_file(temp_path)

            assert not result.valid
            assert result.error_type == "malformed"
            assert "utf-8" in result.error_message.lower()
        finally:
            temp_path.unlink()

    def test_validate_malformed_file_wrong_field_count(self):
        """Test validation of file with wrong number of fields."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write(".youtube.com\tTRUE\t/\tFALSE\t1770778578\n")  # Only 5 fields
            temp_path = Path(f.name)

        try:
            result = CookieValidator.validate_file(temp_path)

            assert not result.valid
            assert result.error_type == "malformed"
            assert "7 tab-separated fields" in result.error_message
        finally:
            temp_path.unlink()

    def test_validate_malformed_file_invalid_expiration(self):
        """Test validation of file with non-numeric expiration."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write(".youtube.com\tTRUE\t/\tFALSE\tINVALID\ttest_cookie\ttest_value\n")
            temp_path = Path(f.name)

        try:
            result = CookieValidator.validate_file(temp_path)

            assert not result.valid
            assert result.error_type == "malformed"
            assert "numeric timestamp" in result.error_message.lower()
        finally:
            temp_path.unlink()

    def test_validate_expired_cookies(self):
        """Test validation of expired cookies."""
        # Create timestamp 30 days in the past
        past_timestamp = int((datetime.now() - timedelta(days=30)).timestamp())

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write(
                f".youtube.com\tTRUE\t/\tFALSE\t{past_timestamp}\ttest_cookie\ttest_value\n"
            )
            temp_path = Path(f.name)

        try:
            result = CookieValidator.validate_file(temp_path)

            assert not result.valid
            assert result.error_type == "expired"
            assert "expired" in result.error_message.lower()
            assert result.days_until_expiry < 0
        finally:
            temp_path.unlink()

    def test_validate_valid_cookies(self):
        """Test validation of valid cookies."""
        # Create timestamp 90 days in the future
        future_timestamp = int((datetime.now() + timedelta(days=90)).timestamp())

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write(
                f".youtube.com\tTRUE\t/\tFALSE\t{future_timestamp}\t__Secure-1PSID\ttest_value\n"
            )
            temp_path = Path(f.name)

        try:
            result = CookieValidator.validate_file(temp_path)

            assert result.valid
            assert result.error_type is None
            assert result.days_until_expiry is not None
            assert 89 <= result.days_until_expiry <= 91  # Allow for timing variance
        finally:
            temp_path.unlink()

    def test_validate_session_cookies_ignored(self):
        """Test that session cookies (expiration=0) are ignored."""
        # Create timestamp 90 days in the future for non-session cookie
        future_timestamp = int((datetime.now() + timedelta(days=90)).timestamp())

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("# Netscape HTTP Cookie File\n")
            # Session cookie (expiration=0)
            f.write(".youtube.com\tTRUE\t/\tFALSE\t0\tPREF\tsession_value\n")
            # Regular cookie with expiration
            f.write(
                f".youtube.com\tTRUE\t/\tTRUE\t{future_timestamp}\t__Secure-1PSID\ttest_value\n"
            )
            temp_path = Path(f.name)

        try:
            result = CookieValidator.validate_file(temp_path)

            assert result.valid
            assert result.days_until_expiry is not None
            # Should use the non-session cookie's expiration
            assert 89 <= result.days_until_expiry <= 91
        finally:
            temp_path.unlink()

    def test_validate_mixed_domains(self):
        """Test validation with both YouTube and non-YouTube domains."""
        future_timestamp = int((datetime.now() + timedelta(days=90)).timestamp())
        far_future_timestamp = int((datetime.now() + timedelta(days=365)).timestamp())

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("# Netscape HTTP Cookie File\n")
            # YouTube cookie (should be checked)
            f.write(
                f".youtube.com\tTRUE\t/\tTRUE\t{future_timestamp}\t__Secure-1PSID\tyt_value\n"
            )
            # Other domain (should be ignored)
            f.write(
                f".example.com\tTRUE\t/\tFALSE\t{far_future_timestamp}\ttest\ttest_value\n"
            )
            temp_path = Path(f.name)

        try:
            result = CookieValidator.validate_file(temp_path)

            assert result.valid
            # Should use YouTube cookie's earlier expiration
            assert 89 <= result.days_until_expiry <= 91
        finally:
            temp_path.unlink()

    def test_validate_comments_and_empty_lines(self):
        """Test that comments and empty lines are properly ignored."""
        future_timestamp = int((datetime.now() + timedelta(days=90)).timestamp())

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write("# This is a comment\n")
            f.write("\n")
            f.write(
                f".youtube.com\tTRUE\t/\tTRUE\t{future_timestamp}\t__Secure-1PSID\ttest_value\n"
            )
            f.write("\n")
            f.write("# Another comment\n")
            temp_path = Path(f.name)

        try:
            result = CookieValidator.validate_file(temp_path)

            assert result.valid
            assert result.days_until_expiry is not None
        finally:
            temp_path.unlink()

    def test_validate_no_expiration_found(self):
        """Test validation when no expiration can be determined."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("# Netscape HTTP Cookie File\n")
            # Only session cookie for non-YouTube domain
            f.write(".example.com\tTRUE\t/\tFALSE\t0\ttest\tvalue\n")
            temp_path = Path(f.name)

        try:
            result = CookieValidator.validate_file(temp_path)

            assert result.valid
            assert "could not determine" in result.error_message.lower()
            assert result.expires_at is None
            assert result.days_until_expiry is None
        finally:
            temp_path.unlink()

    def test_validate_netscape_format_line(self):
        """Test validation of individual lines."""
        # Valid line
        valid, error = CookieValidator.validate_netscape_format(
            ".youtube.com\tTRUE\t/\tFALSE\t1770778578\tPREF\tvalue", 1
        )
        assert valid
        assert error is None

        # Comment line
        valid, error = CookieValidator.validate_netscape_format("# Comment", 2)
        assert valid
        assert error is None

        # Empty line
        valid, error = CookieValidator.validate_netscape_format("", 3)
        assert valid
        assert error is None

        # Invalid secure flag
        valid, error = CookieValidator.validate_netscape_format(
            ".youtube.com\tTRUE\t/\tINVALID\t1770778578\tPREF\tvalue", 4
        )
        assert not valid
        assert "secure flag" in error.lower()


class TestPoTokenValidator:
    """Tests for PO token validation."""

    def test_validate_missing_po_token(self):
        """Test validation with missing PO token."""
        result = CookieValidator.validate_po_token(None)
        assert not result.valid
        assert "missing" in result.error_message.lower()

    def test_validate_empty_po_token(self):
        """Test validation with empty PO token."""
        result = CookieValidator.validate_po_token("")
        assert not result.valid
        assert "missing" in result.error_message.lower()

    def test_validate_whitespace_only_po_token(self):
        """Test validation with whitespace-only PO token."""
        result = CookieValidator.validate_po_token("   ")
        assert not result.valid
        assert "empty" in result.error_message.lower()

    def test_validate_short_po_token(self):
        """Test validation with too-short PO token."""
        result = CookieValidator.validate_po_token("short")
        assert not result.valid
        assert "too short" in result.error_message.lower()

    def test_validate_invalid_characters_po_token(self):
        """Test validation with invalid characters in PO token."""
        result = CookieValidator.validate_po_token("A" * 100 + "!@#$%")
        assert not result.valid
        assert "invalid characters" in result.error_message.lower()

    def test_validate_valid_po_token(self):
        """Test validation with valid PO token."""
        # Valid base64-like string with 120 characters
        result = CookieValidator.validate_po_token("A" * 120)
        assert result.valid
        assert result.error_message is None

    def test_validate_valid_po_token_with_special_chars(self):
        """Test validation with valid PO token containing base64 special chars."""
        # Valid base64 characters including +, /, =, -, _
        result = CookieValidator.validate_po_token(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=-_" * 2
        )
        assert result.valid
        assert result.error_message is None
