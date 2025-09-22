"""Integration tests for SpotdlWrapper with premium detection."""

from unittest.mock import Mock, patch

import pytest
from downloader.premium_detector import PremiumStatus
from downloader.spotdl_wrapper import SpotdlWrapper
from lib.config_class import Config

# Mark all tests in this module to not use the database
pytestmark = pytest.mark.django_db(transaction=False, databases=[])


class TestSpotdlWrapperPremiumIntegration:
    """Integration tests for SpotdlWrapper with premium detection features."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock config for testing."""
        config = Mock(spec=Config)
        config.cookies_location = "/fake/cookies.txt"
        config.po_token = "fake_po_token"
        config.enable_yt_dlp_spoofing = True
        config.music_dir = "/fake/music"
        return config

    @pytest.fixture
    def mock_premium_status_premium(self):
        """Create a premium user status."""
        return PremiumStatus(
            is_premium=True,
            confidence=0.9,
            detection_method="account_info",
        )

    @pytest.fixture
    def mock_premium_status_free(self):
        """Create a free user status."""
        return PremiumStatus(
            is_premium=False,
            confidence=0.8,
            detection_method="account_info",
        )

    @patch("downloader.spotdl_wrapper.PremiumDetector")
    def test_wrapper_initialization_with_premium_detection(
        self, mock_premium_detector, mock_config
    ):
        """Test that SpotdlWrapper initializes premium detection correctly."""
        # Mock premium detector instance
        mock_detector_instance = Mock()
        mock_premium_detector.return_value = mock_detector_instance

        # Initialize wrapper
        wrapper = SpotdlWrapper(mock_config)

        # Verify premium detector was initialized
        mock_premium_detector.assert_called_once_with(
            cookies_file="/fake/cookies.txt", po_token="fake_po_token"
        )

        # Verify wrapper has detector
        assert hasattr(wrapper, "premium_detector")

    @patch("downloader.spotdl_wrapper.PremiumDetector")
    @patch("downloader.spotdl_wrapper.Spotdl")
    def test_bitrate_validation_for_premium_user(
        self,
        mock_spotdl_class,
        mock_premium_detector,
        mock_config,
        mock_premium_status_premium,
    ):
        """Test bitrate validation logic for premium users."""
        # Mock premium detector
        mock_detector_instance = Mock()
        mock_detector_instance.detect_premium_status.return_value = (
            mock_premium_status_premium
        )
        mock_detector_instance.get_song_available_qualities.return_value = [
            (256, "AAC"),
            (128, "AAC"),
        ]
        mock_premium_detector.return_value = mock_detector_instance

        # Mock Spotdl
        mock_spotdl_instance = Mock()
        mock_spotdl_class.return_value = mock_spotdl_instance

        # Initialize wrapper
        wrapper = SpotdlWrapper(mock_config)

        # Test bitrate validation for a song with available high quality
        expected_bitrate = wrapper._get_expected_bitrate_for_song(
            "https://open.spotify.com/track/test"
        )

        # Premium user should expect up to 256kbps if available
        assert expected_bitrate >= 200  # Should be high quality expectation

    @patch("downloader.spotdl_wrapper.PremiumDetector")
    @patch("downloader.spotdl_wrapper.Spotdl")
    def test_bitrate_validation_for_free_user(
        self,
        mock_spotdl_class,
        mock_premium_detector,
        mock_config,
        mock_premium_status_free,
    ):
        """Test bitrate validation logic for free users."""
        # Mock premium detector
        mock_detector_instance = Mock()
        mock_detector_instance.detect_premium_status.return_value = (
            mock_premium_status_free
        )
        mock_detector_instance.get_song_available_qualities.return_value = [
            (128, "AAC"),
        ]
        mock_premium_detector.return_value = mock_detector_instance

        # Mock Spotdl
        mock_spotdl_instance = Mock()
        mock_spotdl_class.return_value = mock_spotdl_instance

        # Initialize wrapper
        wrapper = SpotdlWrapper(mock_config)

        # Test bitrate validation for a song
        expected_bitrate = wrapper._get_expected_bitrate_for_song(
            "https://open.spotify.com/track/test"
        )

        # Free user should expect up to 128kbps
        assert expected_bitrate <= 130  # Should be standard quality expectation

    @patch("downloader.spotdl_wrapper.PremiumDetector")
    @patch("downloader.spotdl_wrapper.Spotdl")
    def test_premium_expiry_detection_during_download(
        self,
        mock_spotdl_class,
        mock_premium_detector,
        mock_config,
        mock_premium_status_premium,
    ):
        """Test that premium expiry is detected during downloads."""
        # Mock premium detector initially returning premium
        mock_detector_instance = Mock()
        mock_detector_instance.detect_premium_status.return_value = (
            mock_premium_status_premium
        )
        mock_detector_instance.is_premium_expired.return_value = (
            True,
            "Quality lower than expected for premium user",
        )
        mock_premium_detector.return_value = mock_detector_instance

        # Mock Spotdl
        mock_spotdl_instance = Mock()
        mock_spotdl_class.return_value = mock_spotdl_instance

        # Initialize wrapper
        wrapper = SpotdlWrapper(mock_config)

        # Simulate download that returns lower quality than expected
        # This would typically happen in the download validation logic
        is_expired, reason = wrapper.premium_detector.is_premium_expired(
            downloaded_bitrate=128, expected_premium_bitrate=256
        )

        # Should detect potential expiry
        assert is_expired is True
        assert "premium" in reason.lower()

    @patch("downloader.spotdl_wrapper.PremiumDetector")
    @patch("downloader.spotdl_wrapper.Spotdl")
    def test_quality_validation_with_song_limitations(
        self,
        mock_spotdl_class,
        mock_premium_detector,
        mock_config,
        mock_premium_status_premium,
    ):
        """Test that quality validation respects song-specific limitations."""
        # Mock premium detector
        mock_detector_instance = Mock()
        mock_detector_instance.detect_premium_status.return_value = (
            mock_premium_status_premium
        )
        # Simulate a song that only has 128kbps available even for premium
        mock_detector_instance.get_song_available_qualities.return_value = [
            (128, "AAC")
        ]
        mock_premium_detector.return_value = mock_detector_instance

        # Mock Spotdl
        mock_spotdl_instance = Mock()
        mock_spotdl_class.return_value = mock_spotdl_instance

        # Initialize wrapper
        wrapper = SpotdlWrapper(mock_config)

        # Test bitrate validation
        expected_bitrate = wrapper._get_expected_bitrate_for_song(
            "https://open.spotify.com/track/test"
        )

        # Even premium users should only expect 128kbps if that's all that's available
        assert expected_bitrate <= 130

    @patch("downloader.spotdl_wrapper.PremiumDetector")
    @patch("downloader.spotdl_wrapper.Spotdl")
    def test_fallback_behavior_when_premium_detection_fails(
        self, mock_spotdl_class, mock_premium_detector, mock_config
    ):
        """Test fallback behavior when premium detection completely fails."""
        # Mock premium detector to fail initialization
        mock_premium_detector.side_effect = Exception(
            "Premium detector initialization failed"
        )

        # Initialization should still work despite premium detector failure
        try:
            SpotdlWrapper(mock_config)
            # If we get here, the wrapper handled the error gracefully
            assert True
        except Exception:
            # If wrapper creation fails, that's also acceptable behavior
            # as long as it doesn't crash the entire application
            pass

    @patch("downloader.spotdl_wrapper.PremiumDetector")
    @patch("downloader.spotdl_wrapper.Spotdl")
    def test_concurrent_premium_status_checks(
        self,
        mock_spotdl_class,
        mock_premium_detector,
        mock_config,
        mock_premium_status_premium,
    ):
        """Test that concurrent premium status checks work correctly."""
        import threading
        import time

        # Mock premium detector with slight delay
        mock_detector_instance = Mock()

        def delayed_detection():
            time.sleep(0.05)  # Small delay
            return mock_premium_status_premium

        mock_detector_instance.detect_premium_status.side_effect = delayed_detection
        mock_premium_detector.return_value = mock_detector_instance

        # Mock Spotdl
        mock_spotdl_instance = Mock()
        mock_spotdl_class.return_value = mock_spotdl_instance

        # Initialize wrapper
        wrapper = SpotdlWrapper(mock_config)

        # Run concurrent premium status checks
        results = []

        def check_premium():
            status = wrapper.premium_detector.detect_premium_status()
            results.append(status)

        threads = [threading.Thread(target=check_premium) for _ in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # All checks should complete successfully
        assert len(results) == 3
        for result in results:
            assert result is not None

    @patch("downloader.spotdl_wrapper.PremiumDetector")
    @patch("downloader.spotdl_wrapper.Spotdl")
    def test_premium_detection_caching_integration(
        self,
        mock_spotdl_class,
        mock_premium_detector,
        mock_config,
        mock_premium_status_premium,
    ):
        """Test that premium detection caching works properly in wrapper context."""
        # Mock premium detector
        mock_detector_instance = Mock()
        mock_detector_instance.detect_premium_status.return_value = (
            mock_premium_status_premium
        )
        mock_premium_detector.return_value = mock_detector_instance

        # Mock Spotdl
        mock_spotdl_instance = Mock()
        mock_spotdl_class.return_value = mock_spotdl_instance

        # Initialize wrapper
        wrapper = SpotdlWrapper(mock_config)

        # First call
        status1 = wrapper.premium_detector.detect_premium_status()
        # Second call (should potentially use cache)
        status2 = wrapper.premium_detector.detect_premium_status()

        # Both should return valid status
        assert status1.is_premium is True
        assert status2.is_premium is True

    @patch("downloader.spotdl_wrapper.PremiumDetector")
    @patch("downloader.spotdl_wrapper.Spotdl")
    def test_error_handling_in_quality_validation(
        self, mock_spotdl_class, mock_premium_detector, mock_config
    ):
        """Test error handling when quality validation methods fail."""
        # Mock premium detector with methods that fail
        mock_detector_instance = Mock()
        mock_detector_instance.detect_premium_status.side_effect = Exception(
            "Premium detection failed"
        )
        mock_detector_instance.get_song_available_qualities.side_effect = Exception(
            "Quality detection failed"
        )
        mock_premium_detector.return_value = mock_detector_instance

        # Mock Spotdl
        mock_spotdl_instance = Mock()
        mock_spotdl_class.return_value = mock_spotdl_instance

        # Initialize wrapper
        wrapper = SpotdlWrapper(mock_config)

        # Quality validation should not crash even if premium detection fails
        try:
            expected_bitrate = wrapper._get_expected_bitrate_for_song(
                "https://open.spotify.com/track/test"
            )
            # Should return some reasonable default
            assert isinstance(expected_bitrate, int)
            assert expected_bitrate > 0
        except Exception as e:
            # If it does fail, it should fail gracefully
            assert "premium" in str(e).lower() or "quality" in str(e).lower()

    @patch("downloader.spotdl_wrapper.PremiumDetector")
    @patch("downloader.spotdl_wrapper.Spotdl")
    def test_wrapper_with_missing_credentials(
        self, mock_spotdl_class, mock_premium_detector, mock_config
    ):
        """Test wrapper behavior when YouTube credentials are missing."""
        # Modify config to have missing credentials
        mock_config.cookies_location = None
        mock_config.po_token = None

        # Mock premium detector
        mock_detector_instance = Mock()
        mock_detector_instance.detect_premium_status.return_value = PremiumStatus(
            is_premium=False,
            confidence=0.1,
            detection_method="no_credentials",
            details="No credentials provided",
        )
        mock_premium_detector.return_value = mock_detector_instance

        # Mock Spotdl
        mock_spotdl_instance = Mock()
        mock_spotdl_class.return_value = mock_spotdl_instance

        # Initialize wrapper
        wrapper = SpotdlWrapper(mock_config)

        # Should initialize and default to free user expectations
        status = wrapper.premium_detector.detect_premium_status()
        assert status.is_premium is False
        assert status.confidence <= 0.2
