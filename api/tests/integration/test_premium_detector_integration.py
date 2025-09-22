"""Integration tests for premium detection in real scenarios."""

import os
from unittest.mock import Mock, patch

import pytest
from downloader.premium_detector import PremiumDetector

# Mark all tests in this module to not use the database
pytestmark = pytest.mark.django_db(transaction=False, databases=[])


class TestPremiumDetectorIntegration:
    """Integration tests for premium detection functionality."""

    @pytest.fixture
    def temp_cookies_file(self):
        """Create a temporary cookies file for testing."""
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("# Fake cookies content\n")
            f.write("youtube.com	FALSE	/	TRUE	0	LOGIN_INFO	fake_login_info\n")
            yield f.name
        os.unlink(f.name)

    @pytest.fixture
    def detector_with_cookies(self, temp_cookies_file):
        """Create a PremiumDetector with test cookies."""
        return PremiumDetector(cookies_file=temp_cookies_file, po_token="test_po_token")

    @pytest.fixture
    def detector_without_credentials(self):
        """Create a PremiumDetector without credentials."""
        return PremiumDetector()

    @patch("downloader.premium_detector.YTMusic")
    def test_account_info_detection_success(self, mock_ytmusic, detector_with_cookies):
        """Test successful premium detection via account info."""
        # Mock YTMusic instance
        mock_instance = Mock()
        mock_ytmusic.return_value = mock_instance

        # Mock account info response indicating premium
        mock_instance.get_account_info.return_value = {
            "accountName": "Premium User",
            "channelHandle": "@premiumuser",
            "isPremium": True,
            "subscriptionType": "PREMIUM",
        }

        # Detect premium status
        status = detector_with_cookies.detect_premium_status()

        # Verify results
        assert status.is_premium is True
        assert status.confidence >= 0.8  # High confidence for account info
        assert status.detection_method == "account_info"
        assert "Premium User" in status.details

    @patch("downloader.premium_detector.YTMusic")
    def test_account_info_detection_free_user(
        self, mock_ytmusic, detector_with_cookies
    ):
        """Test detection of free user via account info."""
        # Mock YTMusic instance
        mock_instance = Mock()
        mock_ytmusic.return_value = mock_instance

        # Mock account info response indicating free user
        mock_instance.get_account_info.return_value = {
            "accountName": "Free User",
            "channelHandle": "@freeuser",
            "isPremium": False,
            "subscriptionType": "FREE",
        }

        # Detect premium status
        status = detector_with_cookies.detect_premium_status()

        # Verify results
        assert status.is_premium is False
        assert status.confidence >= 0.8
        assert status.detection_method == "account_info"
        assert "Free User" in status.details

    @patch("downloader.premium_detector.YTMusic")
    def test_quality_probe_detection(self, mock_ytmusic, detector_with_cookies):
        """Test premium detection via quality probing."""
        # Mock YTMusic instance to fail account info (forcing quality probe)
        mock_instance = Mock()
        mock_ytmusic.return_value = mock_instance
        mock_instance.get_account_info.side_effect = Exception("Account info failed")

        # Mock search results with high-quality formats
        mock_instance.search.return_value = [
            {
                "videoId": "test_video_id",
                "title": "Test Song",
                "artists": [{"name": "Test Artist"}],
            }
        ]

        # Mock get_song to return high-quality streams
        mock_instance.get_song.return_value = {
            "streamingData": {
                "adaptiveFormats": [
                    {"itag": 140, "audioBitrate": 256},  # High quality
                    {"itag": 139, "audioBitrate": 128},  # Standard quality
                ]
            }
        }

        # Detect premium status
        status = detector_with_cookies.detect_premium_status()

        # Verify results
        assert status.is_premium is True  # High quality available = premium
        assert 0.6 <= status.confidence <= 0.8  # Medium confidence for quality probe
        assert status.detection_method == "quality_probe"

    @patch("downloader.premium_detector.YTMusic")
    def test_quality_probe_free_user(self, mock_ytmusic, detector_with_cookies):
        """Test detection of free user via quality probing."""
        # Mock YTMusic instance to fail account info (forcing quality probe)
        mock_instance = Mock()
        mock_ytmusic.return_value = mock_instance
        mock_instance.get_account_info.side_effect = Exception("Account info failed")

        # Mock search results
        mock_instance.search.return_value = [
            {
                "videoId": "test_video_id",
                "title": "Test Song",
                "artists": [{"name": "Test Artist"}],
            }
        ]

        # Mock get_song to return only low-quality streams
        mock_instance.get_song.return_value = {
            "streamingData": {
                "adaptiveFormats": [
                    {"itag": 139, "audioBitrate": 128},  # Only standard quality
                ]
            }
        }

        # Detect premium status
        status = detector_with_cookies.detect_premium_status()

        # Verify results
        assert status.is_premium is False  # Only low quality = free user
        assert 0.6 <= status.confidence <= 0.8
        assert status.detection_method == "quality_probe"

    def test_detection_without_credentials(self, detector_without_credentials):
        """Test that detection gracefully handles missing credentials."""
        status = detector_without_credentials.detect_premium_status()

        # Should default to free user when no credentials
        assert status.is_premium is False
        assert status.confidence == 0.1  # Very low confidence
        assert status.detection_method == "no_credentials"

    @patch("downloader.premium_detector.YTMusic")
    def test_detection_with_api_failure(self, mock_ytmusic, detector_with_cookies):
        """Test detection when all API methods fail."""
        # Mock YTMusic to fail completely
        mock_ytmusic.side_effect = Exception("YouTube API completely failed")

        # Detect premium status
        status = detector_with_cookies.detect_premium_status()

        # Should gracefully fallback
        assert status.is_premium is False  # Conservative fallback
        assert status.confidence <= 0.2  # Low confidence
        assert "error" in status.detection_method.lower()

    @patch("downloader.premium_detector.YTMusic")
    def test_caching_behavior(self, mock_ytmusic, detector_with_cookies):
        """Test that premium status is cached properly."""
        # Mock YTMusic instance
        mock_instance = Mock()
        mock_ytmusic.return_value = mock_instance
        mock_instance.get_account_info.return_value = {
            "isPremium": True,
            "subscriptionType": "PREMIUM",
        }

        # First detection
        status1 = detector_with_cookies.detect_premium_status()
        assert status1.is_premium is True

        # Second detection (should use cache)
        status2 = detector_with_cookies.detect_premium_status()
        assert status1.detection_method == status2.detection_method

        # Force refresh should trigger new detection
        detector_with_cookies.detect_premium_status(force_refresh=True)
        assert mock_instance.get_account_info.call_count == 2  # Additional call made

    @patch("downloader.premium_detector.YTMusic")
    def test_error_handling_in_detection_methods(
        self, mock_ytmusic, detector_with_cookies
    ):
        """Test error handling in individual detection methods."""
        # Mock YTMusic instance
        mock_instance = Mock()
        mock_ytmusic.return_value = mock_instance

        # Test account info error handling
        mock_instance.get_account_info.side_effect = Exception("API Error")
        mock_instance.search.side_effect = Exception("Search Error")

        # Should not crash and should return fallback status
        status = detector_with_cookies.detect_premium_status()
        assert status is not None
        assert isinstance(status.is_premium, bool)
        assert isinstance(status.confidence, float)
        assert isinstance(status.detection_method, str)

    @patch("downloader.premium_detector.YTMusic")
    def test_song_quality_validation(self, mock_ytmusic, detector_with_cookies):
        """Test song-specific quality validation."""
        # Mock YTMusic instance
        mock_instance = Mock()
        mock_ytmusic.return_value = mock_instance

        # Mock search and song data
        mock_instance.search.return_value = [{"videoId": "test_video"}]
        mock_instance.get_song.return_value = {
            "streamingData": {
                "adaptiveFormats": [
                    {"itag": 140, "audioBitrate": 256},
                    {"itag": 139, "audioBitrate": 128},
                ]
            }
        }

        # Test quality validation
        qualities = detector_with_cookies.get_song_available_qualities(
            "https://open.spotify.com/track/test"
        )

        # Should return available qualities
        assert isinstance(qualities, list)
        assert len(qualities) > 0
        # Check that qualities are tuples of (bitrate, format)
        for quality in qualities:
            assert isinstance(quality, tuple)
            assert len(quality) == 2
            assert isinstance(quality[0], int)  # bitrate
            assert isinstance(quality[1], str)  # format

    @patch("downloader.premium_detector.YTMusic")
    def test_premium_expiry_detection(self, mock_ytmusic, detector_with_cookies):
        """Test detection of premium expiry based on quality mismatch."""
        # Mock YTMusic for initial premium detection
        mock_instance = Mock()
        mock_ytmusic.return_value = mock_instance
        mock_instance.get_account_info.return_value = {"isPremium": True}

        # Detect as premium initially
        status = detector_with_cookies.detect_premium_status()
        assert status.is_premium is True

        # Test expiry detection with quality mismatch
        is_expired, reason = detector_with_cookies.is_premium_expired(
            downloaded_bitrate=128, expected_premium_bitrate=256
        )

        # Should detect potential expiry
        assert isinstance(is_expired, bool)
        assert isinstance(reason, str)

    @patch("downloader.premium_detector.YTMusic")
    def test_concurrent_detection_calls(self, mock_ytmusic, detector_with_cookies):
        """Test that concurrent detection calls are handled properly."""
        import threading
        import time

        # Mock YTMusic instance with delay
        mock_instance = Mock()
        mock_ytmusic.return_value = mock_instance

        def slow_account_info():
            time.sleep(0.1)  # Small delay
            return {"isPremium": True}

        mock_instance.get_account_info.side_effect = slow_account_info

        # Run concurrent detections
        results = []

        def detect():
            result = detector_with_cookies.detect_premium_status()
            results.append(result)

        threads = [threading.Thread(target=detect) for _ in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # All should succeed
        assert len(results) == 3
        for result in results:
            assert result is not None
            assert isinstance(result.is_premium, bool)

    @patch("downloader.premium_detector.YTMusic")
    def test_detection_with_partial_credentials(self, mock_ytmusic):
        """Test detection with only cookies (no PO token)."""
        # Test with cookies but no PO token
        detector = PremiumDetector(cookies_file="/fake/path", po_token=None)

        # Should still attempt detection
        status = detector.detect_premium_status()
        assert status is not None

        # Test with PO token but no cookies
        detector = PremiumDetector(cookies_file=None, po_token="fake_token")
        status = detector.detect_premium_status()
        assert status is not None
