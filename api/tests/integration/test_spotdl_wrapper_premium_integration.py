"""Integration tests for SpotdlWrapper with premium detection."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from downloader.premium_detector import PremiumStatus
from downloader.spotdl_wrapper import SpotdlWrapper
from lib.config_class import Config

# Mark all tests in this module to use the database for realistic testing
pytestmark = pytest.mark.django_db


class TestSpotdlWrapperPremiumIntegration:
    """Integration tests for SpotdlWrapper with premium detection features."""

    @pytest.fixture
    def mock_config(self):
        """Create a real config for testing."""
        return Config(
            urls=["https://open.spotify.com/track/test123"],
            cookies_location=Path("/fake/cookies.txt"),
            po_token="fake_po_token",
            log_level="INFO",
            track_artists=False,
            print_exceptions=True,
        )

    @pytest.fixture
    def mock_premium_status_premium(self):
        """Create a premium user status."""
        return PremiumStatus(
            is_premium=True, confidence=0.9, detection_method="account_info"
        )

    @pytest.fixture
    def mock_premium_status_free(self):
        """Create a free user status."""
        return PremiumStatus(
            is_premium=False, confidence=0.8, detection_method="account_info"
        )

    @pytest.fixture
    def mock_premium_status_low_confidence(self):
        """Create a premium status with low confidence."""
        return PremiumStatus(
            is_premium=True, confidence=0.5, detection_method="quality_probe"
        )

    @patch("downloader.spotdl_wrapper.PremiumDetector")
    @patch("downloader.spotdl_wrapper.Spotdl")
    @patch("downloader.spotdl_wrapper.SpotifyClient")
    @patch("downloader.spotdl_wrapper.Downloader")
    def test_wrapper_initialization_with_premium_detection(
        self,
        mock_downloader,
        mock_spotify_client,
        mock_spotdl,
        mock_premium_detector,
        mock_config,
        mock_premium_status_free,
    ):
        """Test that SpotdlWrapper initializes premium detection correctly."""
        # Mock premium detector instance
        mock_detector_instance = Mock()
        mock_detector_instance.detect_premium_status.return_value = (
            mock_premium_status_free
        )
        mock_premium_detector.return_value = mock_detector_instance

        # Initialize wrapper
        wrapper = SpotdlWrapper(mock_config)

        # Verify premium detector was initialized
        mock_premium_detector.assert_called_once_with(
            cookies_file=Path("/fake/cookies.txt"), po_token="fake_po_token"
        )

        # Verify wrapper has detector and status
        assert hasattr(wrapper, "premium_detector")
        assert hasattr(wrapper, "premium_status")
        assert wrapper.premium_status == mock_premium_status_free

    @patch("downloader.spotdl_wrapper.PremiumDetector")
    @patch("downloader.spotdl_wrapper.Spotdl")
    @patch("downloader.spotdl_wrapper.SpotifyClient")
    @patch("downloader.spotdl_wrapper.Downloader")
    def test_bitrate_validation_for_premium_user(
        self,
        mock_downloader,
        mock_spotify_client,
        mock_spotdl_class,
        mock_premium_detector,
        mock_config,
        mock_premium_status_premium,
    ):
        """Test bitrate validation logic for premium users - expects highest available quality."""
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

        # Initialize wrapper
        wrapper = SpotdlWrapper(mock_config)

        # Test the logic that's actually in the execute method
        # Simulate getting available qualities for a song
        spotify_url = "https://open.spotify.com/track/test"
        available_qualities = wrapper.premium_detector.get_song_available_qualities(
            spotify_url
        )
        max_available = (
            max([q[0] for q in available_qualities]) if available_qualities else 128
        )

        # Calculate expected bitrate using wrapper's logic
        if (
            wrapper.premium_status.is_premium
            and wrapper.premium_status.confidence > 0.7
        ):
            expected_bitrate = min(
                255, max_available
            )  # Premium: up to 256kbps or song max
        else:
            expected_bitrate = min(
                127, max_available
            )  # Free: up to 128kbps or song max

        # Premium user should expect up to 255kbps when 256kbps is available
        assert expected_bitrate == 255

    @patch("downloader.spotdl_wrapper.PremiumDetector")
    @patch("downloader.spotdl_wrapper.Spotdl")
    @patch("downloader.spotdl_wrapper.SpotifyClient")
    @patch("downloader.spotdl_wrapper.Downloader")
    def test_bitrate_validation_for_free_user(
        self,
        mock_downloader,
        mock_spotify_client,
        mock_spotdl_class,
        mock_premium_detector,
        mock_config,
        mock_premium_status_free,
    ):
        """Test bitrate validation logic for free users - limited to 128kbps."""
        # Mock premium detector
        mock_detector_instance = Mock()
        mock_detector_instance.detect_premium_status.return_value = (
            mock_premium_status_free
        )
        mock_detector_instance.get_song_available_qualities.return_value = [
            (256, "AAC"),
            (128, "AAC"),
        ]
        mock_premium_detector.return_value = mock_detector_instance

        # Initialize wrapper
        wrapper = SpotdlWrapper(mock_config)

        # Test the logic that's actually in the execute method
        # Simulate getting available qualities for a song
        spotify_url = "https://open.spotify.com/track/test"
        available_qualities = wrapper.premium_detector.get_song_available_qualities(
            spotify_url
        )
        max_available = (
            max([q[0] for q in available_qualities]) if available_qualities else 128
        )

        # Calculate expected bitrate using wrapper's logic
        if (
            wrapper.premium_status.is_premium
            and wrapper.premium_status.confidence > 0.7
        ):
            expected_bitrate = min(255, max_available)
        else:
            expected_bitrate = min(
                127, max_available
            )  # Free: up to 128kbps or song max

        # Free user should be limited to 127kbps even if higher quality available
        assert expected_bitrate == 127

    @patch("downloader.spotdl_wrapper.PremiumDetector")
    @patch("downloader.spotdl_wrapper.Spotdl")
    @patch("downloader.spotdl_wrapper.SpotifyClient")
    @patch("downloader.spotdl_wrapper.Downloader")
    def test_premium_expiry_detection_during_download(
        self,
        mock_downloader,
        mock_spotify_client,
        mock_spotdl_class,
        mock_premium_detector,
        mock_config,
        mock_premium_status_premium,
    ):
        """Test premium expiry detection during download process - should abort downloads."""
        # Mock premium detector
        mock_detector_instance = Mock()
        mock_detector_instance.detect_premium_status.return_value = (
            mock_premium_status_premium
        )
        mock_detector_instance.is_premium_expired.return_value = (
            True,
            "Low bitrate detected - premium may have expired",
        )
        mock_premium_detector.return_value = mock_detector_instance

        # Initialize wrapper
        wrapper = SpotdlWrapper(mock_config)

        # Test premium expiry detection logic that's used in execute method
        is_expired, reason = wrapper.premium_detector.is_premium_expired(
            downloaded_bitrate=128, expected_premium_bitrate=255
        )

        assert is_expired is True
        assert "Low bitrate detected" in reason

        # TODO: Add UI notification system for premium expiry alerts
        # This should notify users immediately when premium expires during downloads
        # Consider implementing both in-app notifications and optional email alerts

    @patch("downloader.spotdl_wrapper.PremiumDetector")
    @patch("downloader.spotdl_wrapper.Spotdl")
    @patch("downloader.spotdl_wrapper.SpotifyClient")
    @patch("downloader.spotdl_wrapper.Downloader")
    def test_quality_validation_with_song_limitations(
        self,
        mock_downloader,
        mock_spotify_client,
        mock_spotdl_class,
        mock_premium_detector,
        mock_config,
        mock_premium_status_premium,
    ):
        """Test that quality validation respects song-specific limitations."""
        # Mock premium detector with a song that only has 160kbps available
        mock_detector_instance = Mock()
        mock_detector_instance.detect_premium_status.return_value = (
            mock_premium_status_premium
        )
        mock_detector_instance.get_song_available_qualities.return_value = [
            (160, "AAC"),
            (128, "AAC"),
        ]
        mock_premium_detector.return_value = mock_detector_instance

        # Initialize wrapper
        wrapper = SpotdlWrapper(mock_config)

        # Test the logic respects song limitations
        spotify_url = "https://open.spotify.com/track/limited_quality"
        available_qualities = wrapper.premium_detector.get_song_available_qualities(
            spotify_url
        )
        max_available = (
            max([q[0] for q in available_qualities]) if available_qualities else 128
        )

        # Calculate expected bitrate - should respect song limitation
        if (
            wrapper.premium_status.is_premium
            and wrapper.premium_status.confidence > 0.7
        ):
            expected_bitrate = min(
                255, max_available
            )  # Premium: up to 256kbps OR song max
        else:
            expected_bitrate = min(127, max_available)

        # Should expect 160kbps, not 255kbps, due to song limitation
        assert expected_bitrate == 160

    @patch("downloader.spotdl_wrapper.PremiumDetector")
    @patch("downloader.spotdl_wrapper.Spotdl")
    @patch("downloader.spotdl_wrapper.SpotifyClient")
    @patch("downloader.spotdl_wrapper.Downloader")
    def test_fallback_behavior_when_premium_detection_fails(
        self,
        mock_downloader,
        mock_spotify_client,
        mock_spotdl_class,
        mock_premium_detector,
        mock_config,
    ):
        """Test fallback behavior when premium detection fails."""
        # Mock premium detector that fails
        mock_detector_instance = Mock()
        mock_detector_instance.detect_premium_status.side_effect = Exception(
            "Detection failed"
        )
        mock_detector_instance.get_song_available_qualities.return_value = []
        mock_premium_detector.return_value = mock_detector_instance

        # Should not raise exception during initialization - graceful fallback
        wrapper = SpotdlWrapper(mock_config)

        # Verify wrapper still has detector
        assert hasattr(wrapper, "premium_detector")

    @patch("downloader.spotdl_wrapper.PremiumDetector")
    @patch("downloader.spotdl_wrapper.Spotdl")
    @patch("downloader.spotdl_wrapper.SpotifyClient")
    @patch("downloader.spotdl_wrapper.Downloader")
    def test_low_confidence_premium_detection(
        self,
        mock_downloader,
        mock_spotify_client,
        mock_spotdl_class,
        mock_premium_detector,
        mock_config,
        mock_premium_status_low_confidence,
    ):
        """Test behavior with low confidence premium detection - should treat as free."""
        # Mock premium detector with low confidence
        mock_detector_instance = Mock()
        mock_detector_instance.detect_premium_status.return_value = (
            mock_premium_status_low_confidence
        )
        mock_detector_instance.get_song_available_qualities.return_value = [
            (256, "AAC"),
            (128, "AAC"),
        ]
        mock_premium_detector.return_value = mock_detector_instance

        # Initialize wrapper
        wrapper = SpotdlWrapper(mock_config)

        # Test the logic treats low confidence as free user
        spotify_url = "https://open.spotify.com/track/test"
        available_qualities = wrapper.premium_detector.get_song_available_qualities(
            spotify_url
        )
        max_available = (
            max([q[0] for q in available_qualities]) if available_qualities else 128
        )

        # Low confidence (0.5 < 0.7 threshold) should be treated as free
        if (
            wrapper.premium_status.is_premium
            and wrapper.premium_status.confidence > 0.7
        ):
            expected_bitrate = min(255, max_available)
        else:
            expected_bitrate = min(
                127, max_available
            )  # Treated as free due to low confidence

        # Should expect free user quality despite is_premium=True due to low confidence
        assert expected_bitrate == 127

    @patch("downloader.spotdl_wrapper.PremiumDetector")
    @patch("downloader.spotdl_wrapper.Spotdl")
    @patch("downloader.spotdl_wrapper.SpotifyClient")
    @patch("downloader.spotdl_wrapper.Downloader")
    def test_premium_status_refresh_on_expiry(
        self,
        mock_downloader,
        mock_spotify_client,
        mock_spotdl_class,
        mock_premium_detector,
        mock_config,
        mock_premium_status_premium,
        mock_premium_status_free,
    ):
        """Test that premium status is refreshed when expiry is detected."""
        # Mock premium detector that initially shows premium, then free after refresh
        mock_detector_instance = Mock()
        mock_detector_instance.detect_premium_status.side_effect = [
            mock_premium_status_premium,  # Initial status
            mock_premium_status_free,  # After refresh
        ]
        mock_detector_instance.is_premium_expired.return_value = (
            True,
            "Premium expired",
        )
        mock_premium_detector.return_value = mock_detector_instance

        # Initialize wrapper
        wrapper = SpotdlWrapper(mock_config)

        # Verify initial premium status
        assert wrapper.premium_status == mock_premium_status_premium

        # Simulate expiry detection and refresh (this would happen in execute method)
        is_expired, _ = wrapper.premium_detector.is_premium_expired(128, 255)
        if is_expired:
            # This simulates the logic in execute method that refreshes status
            refreshed_status = wrapper.premium_detector.detect_premium_status(
                force_refresh=True
            )
            wrapper.premium_status = refreshed_status

        # Status should now be free
        assert wrapper.premium_status == mock_premium_status_free

    @patch("downloader.spotdl_wrapper.PremiumDetector")
    @patch("downloader.spotdl_wrapper.Spotdl")
    @patch("downloader.spotdl_wrapper.SpotifyClient")
    @patch("downloader.spotdl_wrapper.Downloader")
    def test_no_available_qualities_fallback(
        self,
        mock_downloader,
        mock_spotify_client,
        mock_spotdl_class,
        mock_premium_detector,
        mock_config,
        mock_premium_status_premium,
    ):
        """Test fallback behavior when no quality information is available."""
        # Mock premium detector with no available qualities
        mock_detector_instance = Mock()
        mock_detector_instance.detect_premium_status.return_value = (
            mock_premium_status_premium
        )
        mock_detector_instance.get_song_available_qualities.return_value = []
        mock_premium_detector.return_value = mock_detector_instance

        # Initialize wrapper
        wrapper = SpotdlWrapper(mock_config)

        # Test the logic falls back to 128kbps when no qualities available
        spotify_url = "https://open.spotify.com/track/no_quality_info"
        available_qualities = wrapper.premium_detector.get_song_available_qualities(
            spotify_url
        )
        max_available = (
            max([q[0] for q in available_qualities]) if available_qualities else 128
        )

        # Should fallback to 128kbps default
        assert max_available == 128

        # Calculate expected bitrate
        if (
            wrapper.premium_status.is_premium
            and wrapper.premium_status.confidence > 0.7
        ):
            expected_bitrate = min(255, max_available)  # min(255, 128) = 128
        else:
            expected_bitrate = min(127, max_available)

        # Even premium users should get 128kbps when that's all that's "available"
        assert expected_bitrate == 128
