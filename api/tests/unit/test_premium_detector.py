"""Unit tests for premium detection functionality."""

import time
from unittest.mock import Mock, patch

import pytest
from downloader.premium_detector import PremiumDetector, PremiumStatus

# Mark all tests in this module to not use the database
pytestmark = pytest.mark.django_db(transaction=False, databases=[])


class TestPremiumDetector:
    """Test premium detection functionality."""

    @pytest.fixture
    def detector(self):
        """Create a premium detector for testing."""
        return PremiumDetector(cookies_file="/fake/cookies.txt", po_token="fake_token")

    @pytest.fixture
    def mock_ytmusic(self):
        """Create a mock YTMusic client."""
        return Mock()

    def test_premium_status_creation(self):
        """Test PremiumStatus dataclass creation."""
        status = PremiumStatus(
            is_premium=True,
            confidence=0.9,
            detection_method="account_info",
            max_available_bitrate=256,
            last_checked=time.time(),
        )

        assert status.is_premium is True
        assert status.confidence == 0.9
        assert status.detection_method == "account_info"
        assert status.max_available_bitrate == 256
        assert status.error_message is None

    def test_detector_initialization(self, detector):
        """Test premium detector initialization."""
        assert detector.cookies_file == "/fake/cookies.txt"
        assert detector.po_token == "fake_token"
        assert detector._ytmusic_client is None
        assert detector._last_status is None

    @patch("downloader.premium_detector.YTMusic")
    def test_get_ytmusic_client_success(self, mock_ytmusic, detector):
        """Test successful YTMusic client creation."""
        mock_instance = Mock()
        mock_ytmusic.return_value = mock_instance

        client = detector._get_ytmusic_client()

        assert client == mock_instance
        # The actual implementation doesn't call with auth when cookies_file is not JSON
        mock_ytmusic.assert_called_once()
        assert detector._ytmusic_client == mock_instance

    @patch("downloader.premium_detector.YTMusic")
    def test_get_ytmusic_client_failure(self, mock_ytmusic, detector):
        """Test YTMusic client creation failure."""
        mock_ytmusic.side_effect = Exception("Auth failed")

        client = detector._get_ytmusic_client()

        assert client is None
        assert detector._ytmusic_client is None

    def test_get_ytmusic_client_no_cookies(self):
        """Test YTMusic client when no cookies provided."""
        detector = PremiumDetector(cookies_file=None)

        client = detector._get_ytmusic_client()

        # The implementation creates an unauthenticated client as fallback
        assert client is not None

    def test_cache_validation_no_cache(self, detector):
        """Test cache validation when no cache exists."""
        assert not detector._is_cache_valid()

    def test_cache_validation_expired(self, detector):
        """Test cache validation with expired cache."""
        detector._last_status = PremiumStatus(
            is_premium=True,
            confidence=0.9,
            detection_method="test",
            last_checked=time.time() - 2000,  # 2000 seconds ago (expired, >30min)
        )

        assert not detector._is_cache_valid()

    def test_cache_validation_valid(self, detector):
        """Test cache validation with valid cache."""
        detector._last_status = PremiumStatus(
            is_premium=True,
            confidence=0.9,
            detection_method="test",
            last_checked=time.time() - 100,  # 100 seconds ago (valid)
        )

        assert detector._is_cache_valid()

    def test_analyze_account_info_no_data(self, detector):
        """Test account info analysis with no data."""
        result = detector._analyze_account_info({})
        assert result is None

    def test_analyze_account_info_premium_boolean(self, detector):
        """Test account info analysis with boolean premium indicator."""
        account_info = {"isPremium": True}
        result = detector._analyze_account_info(account_info)
        assert result is True

        account_info = {"premium": False}
        result = detector._analyze_account_info(account_info)
        assert result is False

    def test_analyze_account_info_premium_string(self, detector):
        """Test account info analysis with string premium indicator."""
        account_info = {"subscriptionType": "premium"}
        result = detector._analyze_account_info(account_info)
        assert result is True

        account_info = {"membershipType": "free"}
        result = detector._analyze_account_info(account_info)
        assert result is False

        account_info = {"subscription": "youtube_premium"}
        result = detector._analyze_account_info(account_info)
        assert result is True

    @patch.object(PremiumDetector, "_get_ytmusic_client")
    def test_detect_via_account_info_no_client(self, mock_get_client, detector):
        """Test account info detection when client creation fails."""
        mock_get_client.return_value = None

        result = detector._detect_via_account_info()

        assert result.is_premium is False
        assert result.confidence == 0.0
        assert result.detection_method == "account_info_failed"
        assert "Failed to initialize YTMusic client" in result.error_message

    @patch.object(PremiumDetector, "_get_ytmusic_client")
    def test_detect_via_account_info_success(
        self, mock_get_client, detector, mock_ytmusic
    ):
        """Test successful account info detection."""
        mock_get_client.return_value = mock_ytmusic
        mock_ytmusic.get_account_info.return_value = {"isPremium": True}

        result = detector._detect_via_account_info()

        assert result.is_premium is True
        assert result.confidence == 0.9
        assert result.detection_method == "account_info"

    @patch.object(PremiumDetector, "_get_ytmusic_client")
    def test_detect_via_account_info_exception(
        self, mock_get_client, detector, mock_ytmusic
    ):
        """Test account info detection with exception."""
        mock_get_client.return_value = mock_ytmusic
        mock_ytmusic.get_account_info.side_effect = Exception("API Error")

        result = detector._detect_via_account_info()

        assert result.is_premium is False
        assert result.confidence == 0.0
        assert result.detection_method == "account_info_error"
        assert "API Error" in result.error_message

    def test_extract_quality_info_empty(self, detector):
        """Test quality info extraction with empty data."""
        result = detector._extract_quality_info({})
        assert result == []

    def test_extract_quality_info_audio_quality(self, detector):
        """Test quality info extraction with audioQuality fields."""
        song_details = {
            "streamingData": {
                "formats": [
                    {"audioQuality": "AUDIO_QUALITY_HIGH"},
                    {"audioQuality": "AUDIO_QUALITY_MEDIUM"},
                ],
                "adaptiveFormats": [{"audioQuality": "AUDIO_QUALITY_LOW"}],
            }
        }

        result = detector._extract_quality_info(song_details)
        assert sorted(result) == [48, 128, 256]

    def test_extract_quality_info_bitrate(self, detector):
        """Test quality info extraction with direct bitrate fields."""
        song_details = {
            "streamingData": {
                "formats": [
                    {"bitrate": 256000},  # 256 kbps
                    {"bitrate": 128000},  # 128 kbps
                ]
            }
        }

        result = detector._extract_quality_info(song_details)
        assert sorted(result) == [128, 256]

    def test_has_premium_chart_content_empty(self, detector):
        """Test premium chart content detection with empty data."""
        assert not detector._has_premium_chart_content({})

    def test_has_premium_chart_content_premium_indicators(self, detector):
        """Test premium chart content detection with premium indicators."""
        # Test with many chart playlists (premium indicator)
        charts = {
            "countries": {
                "chartPlaylists": [
                    "playlist1",
                    "playlist2",
                    "playlist3",
                    "playlist4",
                    "playlist5",
                    "playlist6",
                ]
            }
        }
        assert detector._has_premium_chart_content(charts)

        # Test with trending section (premium indicator)
        charts = {"trending": {"videos": []}}
        assert detector._has_premium_chart_content(charts)

        # Test with many video playlists (premium indicator)
        charts = {
            "videos": {"playlist": [f"video{i}" for i in range(25)]}  # > 20 videos
        }
        assert detector._has_premium_chart_content(charts)

    def test_get_song_available_qualities_no_client(self):
        """Test getting song qualities when no client available."""
        detector = PremiumDetector(cookies_file=None)

        result = detector.get_song_available_qualities(
            "https://open.spotify.com/track/test"
        )

        # The implementation returns default fallback when no client
        # The actual implementation returns a list of available qualities
        assert isinstance(result, list)
        assert len(result) > 0
        # Check that all items are tuples of (bitrate, format)
        for quality in result:
            assert isinstance(quality, tuple)
            assert len(quality) == 2
            assert isinstance(quality[0], int)  # bitrate
            assert isinstance(quality[1], str)  # format

    @patch.object(PremiumDetector, "_get_ytmusic_client")
    def test_get_song_available_qualities_success(
        self, mock_get_client, detector, mock_ytmusic
    ):
        """Test successful song quality retrieval."""
        mock_get_client.return_value = mock_ytmusic
        mock_ytmusic.search.return_value = [{"videoId": "test123"}]
        mock_ytmusic.get_song.return_value = {
            "streamingData": {
                "formats": [
                    {"audioQuality": "AUDIO_QUALITY_HIGH"},
                    {"audioQuality": "AUDIO_QUALITY_MEDIUM"},
                ]
            }
        }

        result = detector.get_song_available_qualities(
            "https://open.spotify.com/track/test"
        )

        assert result == [(256, "AAC"), (128, "AAC")]

    def test_spotify_url_to_search_query(self, detector):
        """Test Spotify URL to search query conversion."""
        url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
        result = detector._spotify_url_to_search_query(url)
        assert result == "4iV5W9uYEdYUVa79Axb7Rh"

    def test_is_premium_expired_not_premium(self, detector):
        """Test premium expiry check for non-premium account."""
        # When bitrate is below threshold, it will force refresh the status
        # Mock the detect_premium_status to return non-premium
        with patch.object(detector, "detect_premium_status") as mock_detect:
            mock_detect.return_value = PremiumStatus(
                is_premium=False,
                confidence=0.9,
                detection_method="test",
                last_checked=time.time(),
            )

            is_expired, reason = detector.is_premium_expired(128, 240)

            # Should have called detect_premium_status with force_refresh=True
            mock_detect.assert_called_once_with(force_refresh=True)
            assert is_expired is True
            assert "premium expired" in reason.lower()

    def test_is_premium_expired_good_quality(self, detector):
        """Test premium expiry check with good quality download."""
        # High bitrate (250kbps) should return immediately without checking status
        is_expired, reason = detector.is_premium_expired(250, 240)

        assert not is_expired
        assert reason == "Downloaded at expected premium quality"

    def test_is_premium_expired_low_quality_still_premium(self, detector):
        """Test premium expiry check with low quality but account still premium."""
        # Low bitrate (128kbps) but account re-validation shows still premium
        # This means the song just doesn't have higher quality available
        with patch.object(detector, "detect_premium_status") as mock_detect:
            mock_detect.return_value = PremiumStatus(
                is_premium=True,  # Still premium!
                confidence=0.9,
                detection_method="account_info",
                last_checked=time.time(),
            )

            is_expired, reason = detector.is_premium_expired(128, 240)

            # Should have re-validated status
            mock_detect.assert_called_once_with(force_refresh=True)
            # Not expired - song limitation
            assert is_expired is False
            assert "still premium" in reason.lower()
            assert "song limitation" in reason.lower()

    def test_is_premium_expired_low_quality_not_premium(self, detector):
        """Test premium expiry check with low quality and account no longer premium."""
        # Low bitrate (128kbps) and account re-validation shows not premium
        # This means credentials expired
        with patch.object(detector, "detect_premium_status") as mock_detect:
            mock_detect.return_value = PremiumStatus(
                is_premium=False,  # Not premium anymore!
                confidence=0.9,
                detection_method="account_info",
                last_checked=time.time(),
            )

            is_expired, reason = detector.is_premium_expired(128, 240)

            # Should have re-validated status
            mock_detect.assert_called_once_with(force_refresh=True)
            # Expired!
            assert is_expired is True
            assert "premium expired" in reason.lower()

    def test_verify_premium_access_at_startup_success(self, detector):
        """Test startup premium verification when account is premium."""
        with patch.object(detector, "detect_premium_status") as mock_detect:
            mock_detect.return_value = PremiumStatus(
                is_premium=True,
                confidence=0.9,
                detection_method="account_info",
                last_checked=time.time(),
            )

            has_access, message, bitrate = detector.verify_premium_access_at_startup()

            # Should force refresh
            mock_detect.assert_called_once_with(force_refresh=True)
            assert has_access is True
            assert "premium access confirmed" in message.lower()
            assert "account_info" in message.lower()

    def test_verify_premium_access_at_startup_failure(self, detector):
        """Test startup premium verification when account is not premium."""
        with patch.object(detector, "detect_premium_status") as mock_detect:
            mock_detect.return_value = PremiumStatus(
                is_premium=False,
                confidence=0.9,
                detection_method="account_info_error",
                error_message="Authentication failed",
                last_checked=time.time(),
            )

            has_access, message, bitrate = detector.verify_premium_access_at_startup()

            mock_detect.assert_called_once_with(force_refresh=True)
            assert has_access is False
            assert "account status check failed" in message.lower()

    def test_verify_premium_access_at_startup_exception(self, detector):
        """Test startup premium verification when exception occurs."""
        with patch.object(detector, "detect_premium_status") as mock_detect:
            mock_detect.side_effect = Exception("Network error")

            has_access, message, bitrate = detector.verify_premium_access_at_startup()

            assert has_access is False
            assert "premium verification error" in message.lower()

    @patch.object(PremiumDetector, "_detect_via_account_info")
    @patch.object(PremiumDetector, "_detect_via_quality_probe")
    @patch.object(PremiumDetector, "_detect_via_chart_access")
    def test_detect_premium_status_cached(
        self, mock_chart, mock_quality, mock_account, detector
    ):
        """Test premium status detection using cache."""
        # Set up valid cache
        detector._last_status = PremiumStatus(
            is_premium=True,
            confidence=0.9,
            detection_method="cached",
            last_checked=time.time() - 100,  # Valid cache
        )

        result = detector.detect_premium_status()

        assert result == detector._last_status
        # No detection methods should be called
        mock_account.assert_not_called()
        mock_quality.assert_not_called()
        mock_chart.assert_not_called()

    @patch.object(PremiumDetector, "_detect_via_account_info")
    @patch.object(PremiumDetector, "_detect_via_quality_probe")
    @patch.object(PremiumDetector, "_detect_via_chart_access")
    def test_detect_premium_status_force_refresh(
        self, mock_chart, mock_quality, mock_account, detector
    ):
        """Test premium status detection with forced refresh."""
        # Set up valid cache
        detector._last_status = PremiumStatus(
            is_premium=True,
            confidence=0.9,
            detection_method="cached",
            last_checked=time.time() - 100,  # Valid cache
        )

        # Mock high-confidence account detection
        mock_account.return_value = PremiumStatus(
            is_premium=True,
            confidence=0.9,
            detection_method="account_info",
            last_checked=time.time(),
        )

        result = detector.detect_premium_status(force_refresh=True)

        assert result.detection_method == "account_info"
        mock_account.assert_called_once()
        # Other methods shouldn't be called due to high confidence
        mock_quality.assert_not_called()
        mock_chart.assert_not_called()

    @patch.object(PremiumDetector, "_detect_via_account_info")
    @patch.object(PremiumDetector, "_detect_via_quality_probe")
    @patch.object(PremiumDetector, "_detect_via_chart_access")
    def test_detect_premium_status_fallback_methods(
        self, mock_chart, mock_quality, mock_account, detector
    ):
        """Test premium status detection using fallback methods."""
        # Mock low-confidence account detection
        mock_account.return_value = PremiumStatus(
            is_premium=False,
            confidence=0.3,
            detection_method="account_info",
            last_checked=time.time(),
        )

        # Mock higher-confidence quality detection
        mock_quality.return_value = PremiumStatus(
            is_premium=True,
            confidence=0.7,
            detection_method="quality_probe",
            last_checked=time.time(),
        )

        # Mock lower-confidence chart detection
        mock_chart.return_value = PremiumStatus(
            is_premium=True,
            confidence=0.5,
            detection_method="chart_access",
            last_checked=time.time(),
        )

        result = detector.detect_premium_status()

        # Should use quality detection (highest confidence)
        assert result.detection_method == "quality_probe"
        assert result.confidence == 0.7

        # All methods should be called
        mock_account.assert_called_once()
        mock_quality.assert_called_once()
        mock_chart.assert_called_once()
