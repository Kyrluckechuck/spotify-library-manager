"""Integration tests for system health GraphQL API."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from downloader.premium_detector import PoTokenValidationResult
from lib.config_class import Config

from src.schema import schema


@pytest.mark.django_db
@pytest.mark.asyncio
class TestSystemHealthGraphQL:
    """Integration tests for systemHealth GraphQL query."""

    async def test_system_health_query_valid_cookies(self):
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
            # Mock Config to return temp path with valid PO token
            mock_config = MagicMock(spec=Config)
            mock_config.cookies_location = str(temp_path)
            # Valid PO token format (base64-like string, 100+ chars)
            mock_config.po_token = "A" * 120

            # Mock live PO token validation
            mock_po_token_result = PoTokenValidationResult(
                valid=True,
                can_authenticate=True,
            )

            with (
                patch("src.services.system_health.Config", return_value=mock_config),
                patch(
                    "src.services.system_health.PremiumDetector.validate_po_token_live",
                    return_value=mock_po_token_result,
                ),
            ):
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

                result = await schema.execute(query)

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

    async def test_system_health_query_missing_cookies(self):
        """Test systemHealth query with missing cookies."""
        mock_config = MagicMock(spec=Config)
        mock_config.cookies_location = "/nonexistent/cookies.txt"
        mock_config.po_token = "A" * 120

        with patch("src.services.system_health.Config", return_value=mock_config):
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

            result = await schema.execute(query)

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

    async def test_system_health_query_expired_cookies(self):
        """Test systemHealth query with expired cookies."""
        past_timestamp = int((datetime.now() - timedelta(days=30)).timestamp())

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write(
                f".youtube.com\tTRUE\t/\tFALSE\t{past_timestamp}\ttest_cookie\ttest_value\n"
            )
            temp_path = Path(f.name)

        try:
            mock_config = MagicMock(spec=Config)
            mock_config.cookies_location = str(temp_path)
            mock_config.po_token = "A" * 120

            with patch("src.services.system_health.Config", return_value=mock_config):
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

                result = await schema.execute(query)

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

    async def test_system_health_query_malformed_cookies(self):
        """Test systemHealth query with malformed cookies."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write(".youtube.com\tTRUE\t/\tFALSE\t1770778578\n")  # Wrong field count
            temp_path = Path(f.name)

        try:
            mock_config = MagicMock(spec=Config)
            mock_config.cookies_location = str(temp_path)
            mock_config.po_token = "A" * 120

            with patch("src.services.system_health.Config", return_value=mock_config):
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

                result = await schema.execute(query)

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

    async def test_system_health_query_with_queue_status(self):
        """Test systemHealth query along with queueStatus."""
        # Mock Config with valid default path
        mock_config = MagicMock(spec=Config)
        mock_config.cookies_location = "/config/cookies.txt"
        mock_config.po_token = "A" * 120

        # Mock live PO token validation (doesn't matter since cookies won't be valid for /config/cookies.txt)
        mock_po_token_result = PoTokenValidationResult(
            valid=True,
            can_authenticate=True,
        )

        with (
            patch("src.services.system_health.Config", return_value=mock_config),
            patch(
                "src.services.system_health.PremiumDetector.validate_po_token_live",
                return_value=mock_po_token_result,
            ),
        ):
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

            result = await schema.execute(query)

            assert result.errors is None
            assert "systemHealth" in result.data
            assert "queueStatus" in result.data
            assert isinstance(result.data["queueStatus"]["totalPendingTasks"], int)
            assert isinstance(result.data["queueStatus"]["queueSize"], int)
