"""Integration tests for system health GraphQL API."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from django.conf import settings

import pytest

from src.schema import schema


@pytest.mark.django_db
class TestSystemHealthGraphQL:
    """Integration tests for systemHealth GraphQL query."""

    def test_system_health_query_valid_cookies(self):
        """Test systemHealth query with valid cookies."""
        # Create temporary valid cookie file
        future_timestamp = int((datetime.now() + timedelta(days=90)).timestamp())

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write(
                f".youtube.com\tTRUE\t/\tTRUE\t{future_timestamp}\t__Secure-1PSID\ttest_value\n"
            )
            temp_path = Path(f.name)

        try:
            # Patch the cookie file location
            with patch.object(settings, "COOKIE_FILE_PATH", str(temp_path)):
                query = """
                    query {
                        systemHealth {
                            canDownload
                            downloadBlockerReason
                            authentication {
                                cookiesValid
                                cookiesErrorType
                                cookiesErrorMessage
                                cookiesExpireInDays
                                poTokenConfigured
                            }
                        }
                    }
                """

                result = schema.execute_sync(query)

                assert result.errors is None
                assert result.data["systemHealth"]["canDownload"] is True
                assert result.data["systemHealth"]["downloadBlockerReason"] is None
                assert (
                    result.data["systemHealth"]["authentication"]["cookiesValid"]
                    is True
                )
                assert (
                    result.data["systemHealth"]["authentication"]["cookiesErrorType"]
                    is None
                )
                assert (
                    result.data["systemHealth"]["authentication"]["cookiesErrorMessage"]
                    is None
                )
                expire_days = result.data["systemHealth"]["authentication"][
                    "cookiesExpireInDays"
                ]
                assert expire_days is not None
                assert 89 <= expire_days <= 91
        finally:
            temp_path.unlink()

    def test_system_health_query_missing_cookies(self):
        """Test systemHealth query with missing cookies."""
        with patch.object(settings, "COOKIE_FILE_PATH", "/nonexistent/cookies.txt"):
            query = """
                query {
                    systemHealth {
                        canDownload
                        downloadBlockerReason
                        authentication {
                            cookiesValid
                            cookiesErrorType
                            cookiesErrorMessage
                            cookiesExpireInDays
                        }
                    }
                }
            """

            result = schema.execute_sync(query)

            assert result.errors is None
            assert result.data["systemHealth"]["canDownload"] is False
            assert result.data["systemHealth"]["downloadBlockerReason"] is not None
            assert (
                "cookies"
                in result.data["systemHealth"]["downloadBlockerReason"].lower()
            )
            assert (
                result.data["systemHealth"]["authentication"]["cookiesValid"] is False
            )
            assert (
                result.data["systemHealth"]["authentication"]["cookiesErrorType"]
                == "missing"
            )
            assert (
                result.data["systemHealth"]["authentication"]["cookiesErrorMessage"]
                is not None
            )

    def test_system_health_query_expired_cookies(self):
        """Test systemHealth query with expired cookies."""
        past_timestamp = int((datetime.now() - timedelta(days=30)).timestamp())

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write(
                f".youtube.com\tTRUE\t/\tFALSE\t{past_timestamp}\ttest_cookie\ttest_value\n"
            )
            temp_path = Path(f.name)

        try:
            with patch.object(settings, "COOKIE_FILE_PATH", str(temp_path)):
                query = """
                    query {
                        systemHealth {
                            canDownload
                            downloadBlockerReason
                            authentication {
                                cookiesValid
                                cookiesErrorType
                                cookiesErrorMessage
                                cookiesExpireInDays
                            }
                        }
                    }
                """

                result = schema.execute_sync(query)

                assert result.errors is None
                assert result.data["systemHealth"]["canDownload"] is False
                assert (
                    "expired"
                    in result.data["systemHealth"]["downloadBlockerReason"].lower()
                )
                assert (
                    result.data["systemHealth"]["authentication"]["cookiesValid"]
                    is False
                )
                assert (
                    result.data["systemHealth"]["authentication"]["cookiesErrorType"]
                    == "expired"
                )
                expire_days = result.data["systemHealth"]["authentication"][
                    "cookiesExpireInDays"
                ]
                assert expire_days is not None
                assert expire_days < 0
        finally:
            temp_path.unlink()

    def test_system_health_query_malformed_cookies(self):
        """Test systemHealth query with malformed cookies."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write(".youtube.com\tTRUE\t/\tFALSE\t1770778578\n")  # Wrong field count
            temp_path = Path(f.name)

        try:
            with patch.object(settings, "COOKIE_FILE_PATH", str(temp_path)):
                query = """
                    query {
                        systemHealth {
                            canDownload
                            downloadBlockerReason
                            authentication {
                                cookiesValid
                                cookiesErrorType
                                cookiesErrorMessage
                            }
                        }
                    }
                """

                result = schema.execute_sync(query)

                assert result.errors is None
                assert result.data["systemHealth"]["canDownload"] is False
                assert (
                    "malformed"
                    in result.data["systemHealth"]["downloadBlockerReason"].lower()
                )
                assert (
                    result.data["systemHealth"]["authentication"]["cookiesValid"]
                    is False
                )
                assert (
                    result.data["systemHealth"]["authentication"]["cookiesErrorType"]
                    == "malformed"
                )
        finally:
            temp_path.unlink()

    def test_system_health_query_with_queue_status(self):
        """Test systemHealth query along with queueStatus."""
        query = """
            query {
                systemHealth {
                    canDownload
                    authentication {
                        cookiesValid
                    }
                }
                queueStatus {
                    totalPendingTasks
                    queueSize
                }
            }
        """

        result = schema.execute_sync(query)

        assert result.errors is None
        assert "systemHealth" in result.data
        assert "queueStatus" in result.data
        assert isinstance(result.data["queueStatus"]["totalPendingTasks"], int)
        assert isinstance(result.data["queueStatus"]["queueSize"], int)
