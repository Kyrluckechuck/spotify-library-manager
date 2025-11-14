"""Premium detection service for YouTube Music accounts."""

import json
import logging
import time
from dataclasses import dataclass
from http.cookiejar import MozillaCookieJar
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
    details: Optional[str] = None  # Additional details about the detection


@dataclass
class PoTokenValidationResult:
    """Result of live PO token validation against YouTube API."""

    valid: bool
    error_message: Optional[str] = None
    last_checked: Optional[float] = None
    can_authenticate: bool = False
    details: Optional[str] = None


class PremiumDetector:
    """Detects YouTube Music premium status using multiple methods."""

    def __init__(
        self,
        cookies_file: Optional[str] = None,
        po_token: Optional[str] = None,
        ytmusic_headers_file: Optional[str] = None,
    ):
        """
        Initialize the premium detector.

        Args:
            cookies_file: Path to YouTube cookies file (used by yt-dlp for downloads)
            po_token: YouTube po_token for authentication
            ytmusic_headers_file: Optional path to YTMusic JSON headers file for premium detection
        """
        self.logger = logging.getLogger(__name__)
        self.cookies_file = cookies_file
        self.po_token = po_token
        self.ytmusic_headers_file = ytmusic_headers_file
        self._ytmusic_client: Optional[YTMusic] = None
        self._last_status: Optional[PremiumStatus] = None
        self._last_po_token_validation: Optional[PoTokenValidationResult] = None
        self._cache_duration = 1800  # 30 minutes cache

    def _get_ytmusic_client(self) -> Optional[YTMusic]:
        """Get or create YTMusic client with authentication priority."""
        if self._ytmusic_client is None:
            try:
                # Priority 1: Dedicated YTMusic headers file
                if self.ytmusic_headers_file and self._is_json_auth_file(
                    str(self.ytmusic_headers_file)
                ):
                    self._ytmusic_client = YTMusic(auth=str(self.ytmusic_headers_file))
                    self.logger.debug(
                        "YTMusic client initialized with dedicated headers file"
                    )
                    return self._ytmusic_client

                # Priority 2: Check if cookies_file is actually a JSON auth file
                elif self.cookies_file and self._is_json_auth_file(
                    str(self.cookies_file)
                ):
                    self._ytmusic_client = YTMusic(auth=str(self.cookies_file))
                    self.logger.debug(
                        "YTMusic client initialized with JSON auth from cookies_file"
                    )
                    return self._ytmusic_client

                # Priority 3: Try to convert cookies to headers using setup_browser
                elif self.cookies_file:
                    self.logger.info(
                        "Attempting to convert cookies to YTMusic authentication..."
                    )
                    auth_content = self._convert_cookies_to_ytmusic_headers(
                        str(self.cookies_file)
                    )
                    if auth_content:
                        # setup_browser returns JSON string that can be used directly
                        self._ytmusic_client = YTMusic(auth=auth_content)
                        self.logger.info(
                            "YTMusic client initialized with converted cookie authentication"
                        )
                        return self._ytmusic_client
                    else:
                        self.logger.warning(
                            "Cookie conversion failed, falling back to unauthenticated client"
                        )

                # Priority 4: Unauthenticated fallback (limited premium detection)
                self._ytmusic_client = YTMusic()
                self.logger.info(
                    "YTMusic client initialized without authentication (limited premium detection capabilities)"
                )

            except Exception as e:
                self.logger.warning(f"Failed to initialize YTMusic client: {e}")
                # Final fallback
                try:
                    self._ytmusic_client = YTMusic()
                    self.logger.debug(
                        "Emergency fallback to unauthenticated YTMusic client"
                    )
                except Exception as fallback_e:
                    self.logger.error(
                        f"Complete YTMusic initialization failure: {fallback_e}"
                    )
                    return None
        return self._ytmusic_client

    def _is_json_auth_file(self, file_path: str) -> bool:
        """Check if the file is a JSON authentication file (not Netscape cookies)."""
        try:
            with open(file_path, "r") as f:
                content = f.read().strip()
                if content.startswith("# Netscape HTTP Cookie File"):
                    return False
                json.loads(content)
                return True
        except (json.JSONDecodeError, FileNotFoundError, OSError):
            return False

    def _convert_cookies_to_ytmusic_headers(self, cookies_file: str) -> Optional[str]:
        """Convert Netscape cookies to YTMusic-compatible headers using setup_browser method."""
        try:
            import json

            from ytmusicapi.auth.browser import (
                get_authorization,
                sapisid_from_cookie,
                setup_browser,
            )

            # Load cookies from Netscape format
            cookie_jar = MozillaCookieJar(cookies_file)
            cookie_jar.load(ignore_discard=True, ignore_expires=True)

            # Convert cookies to cookie header string
            cookie_header = "; ".join([f"{c.name}={c.value}" for c in cookie_jar])

            if not cookie_header:
                self.logger.warning("No cookies found in cookie file")
                return None

            # Create raw headers string in the format YTMusic setup_browser expects
            # This mimics the headers you'd see in Firefox network inspector
            headers_raw = f"""Host: music.youtube.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Content-Type: application/json
x-goog-authuser: 0
x-origin: https://music.youtube.com
Cookie: {cookie_header}
Connection: keep-alive"""

            # Use YTMusic's setup_browser to create proper auth file
            auth_file_content = setup_browser(headers_raw=headers_raw)

            # Parse the auth file and add the authorization header for browser detection
            auth_data = json.loads(auth_file_content)

            # Extract SAPISID from cookies and generate authorization header
            try:
                sapisid = sapisid_from_cookie(cookie_header)
                auth_header = get_authorization(f"{sapisid} https://music.youtube.com")
                auth_data["authorization"] = auth_header

                # Return the modified auth content
                modified_auth_content = json.dumps(auth_data)
                self.logger.debug(
                    "Successfully converted cookies to YTMusic auth with authorization header"
                )
                return modified_auth_content

            except Exception as auth_error:
                self.logger.warning(
                    f"Failed to generate authorization header: {auth_error}"
                )
                # Return original auth content without authorization
                return auth_file_content

        except Exception as e:
            self.logger.warning(f"Failed to convert cookies to YTMusic headers: {e}")
            return None

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
            # Type checker: _last_status is guaranteed non-None here because _is_cache_valid checks it
            assert self._last_status is not None
            return self._last_status

        self.logger.info("Detecting YouTube Music premium status...")

        # If no credentials provided, return low confidence free status
        if (
            not self.cookies_file
            and not self.po_token
            and not self.ytmusic_headers_file
        ):
            status = PremiumStatus(
                is_premium=False,
                confidence=0.1,
                detection_method="no_credentials",
                last_checked=time.time(),
            )
            self._last_status = status
            return status

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

    def validate_po_token_live(
        self, force_refresh: bool = False
    ) -> PoTokenValidationResult:
        """
        Validate PO token by actually testing it against YouTube Music API.

        This performs a lightweight API call to verify the PO token works.
        Results are cached for 30 minutes to avoid hammering YouTube.

        Args:
            force_refresh: If True, bypass cache and re-validate

        Returns:
            PoTokenValidationResult with validation status and details
        """
        # Check cache first
        if not force_refresh and self._is_po_token_cache_valid():
            # Type checker: _last_po_token_validation is guaranteed non-None here
            assert self._last_po_token_validation is not None
            return self._last_po_token_validation

        self.logger.info("Validating PO token against YouTube Music API...")

        # If no PO token provided, return invalid
        if not self.po_token:
            result = PoTokenValidationResult(
                valid=False,
                error_message="PO token not provided",
                last_checked=time.time(),
                can_authenticate=False,
            )
            self._last_po_token_validation = result
            return result

        # Try to create YTMusic client with credentials
        client = self._get_ytmusic_client()
        if not client:
            result = PoTokenValidationResult(
                valid=False,
                error_message="Failed to initialize YTMusic client with provided credentials",
                last_checked=time.time(),
                can_authenticate=False,
                details="Check that cookies file exists and is valid",
            )
            self._last_po_token_validation = result
            return result

        # Test authentication by trying to get account info
        try:
            account_info = client.get_account_info()
            if account_info and account_info.get("accountName"):
                # Successfully authenticated
                result = PoTokenValidationResult(
                    valid=True,
                    last_checked=time.time(),
                    can_authenticate=True,
                    details=f"Authenticated as: {account_info.get('accountName', 'Unknown')}",
                )
                self.logger.info(
                    f"PO token validated successfully. Account: {account_info.get('accountName')}"
                )
            else:
                # Got response but no account info - might be unauthenticated
                result = PoTokenValidationResult(
                    valid=False,
                    error_message="PO token may be invalid - could not retrieve account information",
                    last_checked=time.time(),
                    can_authenticate=False,
                    details="API returned empty or incomplete account info",
                )
                self.logger.warning(
                    "PO token validation unclear - no account info returned"
                )

        except Exception as e:
            # Authentication failed
            error_str = str(e).lower()
            if (
                "unauthorized" in error_str
                or "forbidden" in error_str
                or "401" in error_str
                or "403" in error_str
            ):
                error_message = (
                    "PO token appears to be invalid or expired - authentication failed"
                )
                details = f"YouTube API error: {str(e)}"
            else:
                error_message = "Failed to validate PO token due to API error"
                details = f"Error: {str(e)}"

            result = PoTokenValidationResult(
                valid=False,
                error_message=error_message,
                last_checked=time.time(),
                can_authenticate=False,
                details=details,
            )
            self.logger.warning(
                f"PO token validation failed: {error_message} - {details}"
            )

        self._last_po_token_validation = result
        return result

    def _is_po_token_cache_valid(self) -> bool:
        """Check if cached PO token validation is still valid."""
        if (
            self._last_po_token_validation is None
            or self._last_po_token_validation.last_checked is None
        ):
            return False
        return (
            time.time() - self._last_po_token_validation.last_checked
            < self._cache_duration
        )

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
                details=(
                    account_info.get("accountName", "Unknown User")
                    if account_info
                    else None
                ),
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
                        confidence = 0.7 if max_bitrate > 128 else 0.3

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
                confidence=0.1,
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
        self, downloaded_bitrate: int, expected_premium_bitrate: int = 240
    ) -> Tuple[bool, str]:
        """
        Check if premium has expired based on downloaded bitrate.

        When low bitrate is detected, forces a fresh account status check
        against YouTube API to determine if credentials actually expired
        vs the song just having lower quality available.

        Args:
            downloaded_bitrate: Actual bitrate of downloaded file
            expected_premium_bitrate: Expected bitrate for premium users (default 240kbps)

        Returns:
            Tuple of (is_expired, reason)
        """
        # If we got expected premium quality, all good
        if downloaded_bitrate >= expected_premium_bitrate:
            return False, "Downloaded at expected premium quality"

        # Low bitrate detected - force fresh account check (bypass cache)
        self.logger.info(
            f"Low bitrate detected ({downloaded_bitrate}kbps < {expected_premium_bitrate}kbps), "
            f"re-validating premium status..."
        )
        status = self.detect_premium_status(force_refresh=True)

        if not status.is_premium:
            # Account info confirms we're NOT premium anymore
            return True, (
                f"YouTube account info confirms premium expired - "
                f"got {downloaded_bitrate}kbps (expected {expected_premium_bitrate}kbps+)"
            )

        # Account still shows premium but got low bitrate - probably song limitation
        self.logger.info(
            f"Account info confirms still premium despite {downloaded_bitrate}kbps - "
            f"likely this song's maximum quality"
        )
        return False, (
            f"Downloaded at {downloaded_bitrate}kbps but account info confirms "
            f"still premium - likely song limitation"
        )

    def verify_premium_access_at_startup(self) -> Tuple[bool, str, Optional[int]]:
        """
        Verify premium access at startup using a known high-quality test track.

        Uses a YouTube Music track known to have 258kbps premium quality available.
        This provides early detection of expired credentials before downloading
        user's actual library.

        Returns:
            Tuple of (has_premium_access, message, bitrate_achieved)
        """
        self.logger.info("Verifying premium access at startup...")

        try:
            # First, check account status via API
            status = self.detect_premium_status(force_refresh=True)

            if not status.is_premium:
                return (
                    False,
                    (
                        f"Account status check failed: {status.detection_method} - "
                        f"{status.error_message or 'Not premium'}"
                    ),
                    None,
                )

            # Account API says we're premium, return success
            self.logger.info(
                f"Premium status verified via {status.detection_method} "
                f"(confidence: {status.confidence})"
            )
            return (
                True,
                (
                    f"Premium access confirmed via {status.detection_method} "
                    f"(confidence: {status.confidence:.2f})"
                ),
                None,
            )

        except Exception as e:
            self.logger.error(f"Premium verification failed: {e}")
            return False, f"Premium verification error: {str(e)}", None
