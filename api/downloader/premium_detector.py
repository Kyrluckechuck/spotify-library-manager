"""Premium detection service for YouTube Music accounts."""

import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ytmusicapi import YTMusic


@dataclass
class PremiumStatus:
    """Represents the premium status of a YouTube Music account."""

    is_premium: bool
    confidence: float  # 0.0 to 1.0
    detection_method: str
    max_available_bitrate: Optional[int] = None
    last_checked: Optional[float] = None
    error_message: Optional[str] = None


class PremiumDetector:
    """Detects YouTube Music premium status using multiple methods."""

    def __init__(
        self, cookies_file: Optional[str] = None, po_token: Optional[str] = None
    ):
        """
        Initialize the premium detector.

        Args:
            cookies_file: Path to YouTube cookies file
            po_token: YouTube po_token for authentication
        """
        self.logger = logging.getLogger(__name__)
        self.cookies_file = cookies_file
        self.po_token = po_token
        self._ytmusic_client: Optional[YTMusic] = None
        self._last_status: Optional[PremiumStatus] = None
        self._cache_duration = 300  # 5 minutes cache

    def _get_ytmusic_client(self) -> Optional[YTMusic]:
        """Get or create YTMusic client."""
        if self._ytmusic_client is None and self.cookies_file:
            try:
                # Convert Path object to string if needed
                cookies_path = str(self.cookies_file)
                # Initialize YTMusic with cookies for authentication
                self._ytmusic_client = YTMusic(auth=cookies_path)
                self.logger.debug("YTMusic client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize YTMusic client: {e}")
                return None
        return self._ytmusic_client

    def detect_premium_status(self, force_refresh: bool = False) -> PremiumStatus:
        """
        Detect premium status using multiple methods.

        Args:
            force_refresh: Force a fresh check, bypassing cache

        Returns:
            PremiumStatus object with detection results
        """
        # Check cache first
        if not force_refresh and self._is_cache_valid():
            return self._last_status

        self.logger.info("Detecting YouTube Music premium status...")

        # Method 1: Try account info detection
        status = self._detect_via_account_info()
        if status.confidence >= 0.8:
            self._last_status = status
            return status

        # Method 2: Try quality probe detection
        quality_status = self._detect_via_quality_probe()
        if quality_status.confidence > status.confidence:
            status = quality_status

        # Method 3: Try chart access detection as fallback
        chart_status = self._detect_via_chart_access()
        if chart_status.confidence > status.confidence:
            status = chart_status

        self._last_status = status
        return status

    def _is_cache_valid(self) -> bool:
        """Check if cached status is still valid."""
        if self._last_status is None or self._last_status.last_checked is None:
            return False
        return time.time() - self._last_status.last_checked < self._cache_duration

    def _detect_via_account_info(self) -> PremiumStatus:
        """Detect premium status via account info API."""
        client = self._get_ytmusic_client()
        if not client:
            return PremiumStatus(
                is_premium=False,
                confidence=0.0,
                detection_method="account_info_failed",
                error_message="Failed to initialize YTMusic client",
                last_checked=time.time(),
            )

        try:
            account_info = client.get_account_info()
            self.logger.debug(f"Account info retrieved: {account_info}")

            # Look for premium indicators in account info
            is_premium = self._analyze_account_info(account_info)
            confidence = 0.9 if is_premium is not None else 0.0

            return PremiumStatus(
                is_premium=is_premium or False,
                confidence=confidence,
                detection_method="account_info",
                last_checked=time.time(),
            )

        except Exception as e:
            self.logger.warning(f"Account info detection failed: {e}")
            return PremiumStatus(
                is_premium=False,
                confidence=0.0,
                detection_method="account_info_error",
                error_message=str(e),
                last_checked=time.time(),
            )

    def _analyze_account_info(self, account_info: Dict) -> Optional[bool]:
        """
        Analyze account info for premium indicators.

        Args:
            account_info: Raw account info from YTMusic API

        Returns:
            True if premium detected, False if free, None if uncertain
        """
        if not account_info:
            return None

        # Look for premium-specific fields
        premium_indicators = [
            "subscriptionType",
            "premium",
            "isPremium",
            "membershipType",
            "subscription",
        ]

        for indicator in premium_indicators:
            if indicator in account_info:
                value = account_info[indicator]
                if isinstance(value, bool):
                    return value
                elif isinstance(value, str):
                    premium_values = [
                        "premium",
                        "paid",
                        "music_premium",
                        "youtube_premium",
                    ]
                    return value.lower() in premium_values

        return None

    def _detect_via_quality_probe(self) -> PremiumStatus:
        """Detect premium status by probing available quality formats."""
        client = self._get_ytmusic_client()
        if not client:
            return PremiumStatus(
                is_premium=False,
                confidence=0.0,
                detection_method="quality_probe_failed",
                last_checked=time.time(),
            )

        try:
            # Search for a popular song to test quality
            test_queries = [
                "The Beatles - Hey Jude",
                "Ed Sheeran - Shape of You",
                "Billie Eilish - Bad Guy",
            ]

            for query in test_queries:
                try:
                    search_results = client.search(query, filter="songs", limit=1)
                    if not search_results:
                        continue

                    song = search_results[0]
                    video_id = song.get("videoId")
                    if not video_id:
                        continue

                    # Try to get song details which might include quality info
                    song_details = client.get_song(video_id)
                    quality_info = self._extract_quality_info(song_details)

                    if quality_info:
                        max_bitrate = max(quality_info) if quality_info else 128
                        is_premium = max_bitrate > 128
                        confidence = 0.7 if max_bitrate > 128 else 0.6

                        return PremiumStatus(
                            is_premium=is_premium,
                            confidence=confidence,
                            detection_method="quality_probe",
                            max_available_bitrate=max_bitrate,
                            last_checked=time.time(),
                        )

                except Exception as e:
                    self.logger.debug(f"Quality probe failed for '{query}': {e}")
                    continue

            return PremiumStatus(
                is_premium=False,
                confidence=0.3,
                detection_method="quality_probe_inconclusive",
                last_checked=time.time(),
            )

        except Exception as e:
            self.logger.warning(f"Quality probe detection failed: {e}")
            return PremiumStatus(
                is_premium=False,
                confidence=0.0,
                detection_method="quality_probe_error",
                error_message=str(e),
                last_checked=time.time(),
            )

    def _extract_quality_info(self, song_details: Dict) -> List[int]:
        """Extract available quality bitrates from song details."""
        quality_list = []

        # Look for streaming data or format information
        streaming_data = song_details.get("streamingData", {})
        formats = streaming_data.get("formats", [])
        formats.extend(streaming_data.get("adaptiveFormats", []))

        for format_info in formats:
            if "audioQuality" in format_info:
                # Map YouTube audio quality to approximate bitrates
                quality_map = {
                    "AUDIO_QUALITY_LOW": 48,
                    "AUDIO_QUALITY_MEDIUM": 128,
                    "AUDIO_QUALITY_HIGH": 256,
                }
                quality = format_info["audioQuality"]
                if quality in quality_map:
                    quality_list.append(quality_map[quality])

            elif "bitrate" in format_info:
                # Direct bitrate information
                bitrate = format_info["bitrate"]
                if isinstance(bitrate, int):
                    quality_list.append(bitrate // 1000)  # Convert to kbps

        return quality_list

    def _detect_via_chart_access(self) -> PremiumStatus:
        """Detect premium status by accessing premium-only chart features."""
        client = self._get_ytmusic_client()
        if not client:
            return PremiumStatus(
                is_premium=False,
                confidence=0.0,
                detection_method="chart_access_failed",
                last_checked=time.time(),
            )

        try:
            # Try to access premium-only chart features
            charts = client.get_charts()

            # Look for premium-specific chart content
            has_premium_charts = self._has_premium_chart_content(charts)
            confidence = 0.8 if has_premium_charts else 0.4

            return PremiumStatus(
                is_premium=has_premium_charts,
                confidence=confidence,
                detection_method="chart_access",
                last_checked=time.time(),
            )

        except Exception as e:
            self.logger.debug(f"Chart access detection failed: {e}")
            return PremiumStatus(
                is_premium=False,
                confidence=0.0,
                detection_method="chart_access_error",
                error_message=str(e),
                last_checked=time.time(),
            )

    def _has_premium_chart_content(self, charts: Dict) -> bool:
        """Check if charts contain premium-only content."""
        if not charts:
            return False

        # Premium users get access to more detailed chart information
        premium_indicators = [
            len(charts.get("countries", {}).get("chartPlaylists", [])) > 5,
            "trending" in charts,
            len(charts.get("videos", {}).get("playlist", [])) > 20,
        ]

        return any(premium_indicators)

    def get_song_available_qualities(self, spotify_url: str) -> List[Tuple[int, str]]:
        """
        Get available quality options for a specific song.

        Args:
            spotify_url: Spotify URL to check

        Returns:
            List of tuples: (bitrate_kbps, format_name)
        """
        client = self._get_ytmusic_client()
        if not client:
            return [(128, "AAC")]  # Default fallback

        try:
            # Convert Spotify URL to search query and find the song
            search_query = self._spotify_url_to_search_query(spotify_url)
            search_results = client.search(search_query, filter="songs", limit=5)

            for song in search_results:
                video_id = song.get("videoId")
                if not video_id:
                    continue

                song_details = client.get_song(video_id)
                qualities = self._extract_quality_info(song_details)

                if qualities:
                    # Return available qualities with format names
                    return [
                        (q, "AAC" if q <= 256 else "Opus")
                        for q in sorted(qualities, reverse=True)
                    ]

        except Exception as e:
            self.logger.debug(f"Failed to get song qualities for {spotify_url}: {e}")

        return [(128, "AAC")]  # Default fallback

    def _spotify_url_to_search_query(self, spotify_url: str) -> str:
        """Convert Spotify URL to search query (placeholder)."""
        # This should integrate with your existing Spotify metadata extraction
        # For now, return a basic search query
        return spotify_url.split("/")[-1]  # Simplified

    def is_premium_expired(
        self, downloaded_bitrate: int, expected_premium_bitrate: int = 256
    ) -> Tuple[bool, str]:
        """
        Check if premium has expired based on downloaded bitrate vs expected.

        Args:
            downloaded_bitrate: Actual bitrate of downloaded file
            expected_premium_bitrate: Expected bitrate for premium users

        Returns:
            Tuple of (is_expired, reason)
        """
        status = self.detect_premium_status()

        if not status.is_premium:
            return False, "Account is not premium"

        if downloaded_bitrate >= expected_premium_bitrate:
            return False, "Downloaded at expected premium quality"

        # Check if this song actually has higher quality available
        # This would need song URL - placeholder for now
        if downloaded_bitrate == 128:
            return True, (
                f"Premium account but only got {downloaded_bitrate}kbps "
                f"(expected {expected_premium_bitrate}kbps)"
            )

        return False, (
            f"Downloaded at {downloaded_bitrate}kbps which may be "
            f"max available for this song"
        )
