"""Unit tests for validation module."""

from api.library_manager.validation import (
    extract_spotify_id,
    get_spotify_url_type,
    is_spotify_album_url,
    is_spotify_playlist_url,
    is_spotify_track_url,
    validate_spotify_url,
)


class TestValidationFunctions:
    """Test validation utility functions."""

    def test_validate_spotify_url_valid(self):
        """Test valid Spotify URL validation."""
        valid_urls = [
            "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
            "https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy",
            "https://open.spotify.com/artist/0TnOYISbd1XYRBk9myaseg",
            "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
            "spotify:track:4iV5W9uYEdYUVa79Axb7Rh",
            "spotify:album:4aawyAB9vmqN3uQ7FjRGTy",
            "spotify:artist:0TnOYISbd1XYRBk9myaseg",
            "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M",
        ]

        for url in valid_urls:
            is_valid, error = validate_spotify_url(url)
            assert is_valid is True, f"URL {url} should be valid: {error}"

    def test_validate_spotify_url_invalid(self):
        """Test invalid Spotify URL validation."""
        invalid_urls = [
            "invalid:url",
            "http://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
            "https://example.com",
            "",
        ]

        for url in invalid_urls:
            is_valid, error = validate_spotify_url(url)
            assert is_valid is False, f"URL {url} should be invalid"
            assert error is not None

    def test_extract_spotify_id_valid(self):
        """Test extracting Spotify ID from valid URLs."""
        test_cases = [
            (
                "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
                "4iV5W9uYEdYUVa79Axb7Rh",
            ),
            (
                "https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy",
                "4aawyAB9vmqN3uQ7FjRGTy",
            ),
            (
                "https://open.spotify.com/artist/0TnOYISbd1XYRBk9myaseg",
                "0TnOYISbd1XYRBk9myaseg",
            ),
            ("spotify:track:4iV5W9uYEdYUVa79Axb7Rh", "4iV5W9uYEdYUVa79Axb7Rh"),
            ("spotify:album:4aawyAB9vmqN3uQ7FjRGTy", "4aawyAB9vmqN3uQ7FjRGTy"),
        ]

        for url, expected_id in test_cases:
            extracted_id = extract_spotify_id(url)
            assert (
                extracted_id == expected_id
            ), f"Expected {expected_id}, got {extracted_id} for {url}"

    def test_extract_spotify_id_invalid(self):
        """Test extracting Spotify ID from invalid URLs."""
        invalid_urls = ["invalid:url", "https://example.com", ""]

        for url in invalid_urls:
            extracted_id = extract_spotify_id(url)
            assert (
                extracted_id is None
            ), f"Should return None for {url}, got {extracted_id}"

    def test_is_spotify_playlist_url(self):
        """Test playlist URL detection."""
        playlist_urls = [
            "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
            "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M",
            "https://open.spotify.com/playlist/123",
        ]

        non_playlist_urls = [
            "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
            "https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy",
            "https://open.spotify.com/artist/0TnOYISbd1XYRBk9myaseg",
        ]

        for url in playlist_urls:
            assert (
                is_spotify_playlist_url(url) is True
            ), f"{url} should be detected as playlist"

        for url in non_playlist_urls:
            assert (
                is_spotify_playlist_url(url) is False
            ), f"{url} should not be detected as playlist"

    def test_is_spotify_album_url(self):
        """Test album URL detection."""
        album_urls = [
            "https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy",
            "spotify:album:4aawyAB9vmqN3uQ7FjRGTy",
            "https://open.spotify.com/album/123",
        ]

        non_album_urls = [
            "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
            "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
            "https://open.spotify.com/artist/0TnOYISbd1XYRBk9myaseg",
        ]

        for url in album_urls:
            assert (
                is_spotify_album_url(url) is True
            ), f"{url} should be detected as album"

        for url in non_album_urls:
            assert (
                is_spotify_album_url(url) is False
            ), f"{url} should not be detected as album"

    def test_is_spotify_track_url(self):
        """Test track URL detection."""
        track_urls = [
            "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh",
            "spotify:track:4iV5W9uYEdYUVa79Axb7Rh",
            "https://open.spotify.com/track/123",
        ]

        non_track_urls = [
            "https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy",
            "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
            "https://open.spotify.com/artist/0TnOYISbd1XYRBk9myaseg",
        ]

        for url in track_urls:
            assert (
                is_spotify_track_url(url) is True
            ), f"{url} should be detected as track"

        for url in non_track_urls:
            assert (
                is_spotify_track_url(url) is False
            ), f"{url} should not be detected as track"

    def test_get_spotify_url_type(self):
        """Test URL type detection."""
        test_cases = [
            ("https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh", "track"),
            ("https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy", "album"),
            ("https://open.spotify.com/artist/0TnOYISbd1XYRBk9myaseg", "artist"),
            ("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M", "playlist"),
            ("spotify:track:4iV5W9uYEdYUVa79Axb7Rh", "track"),
            ("spotify:album:4aawyAB9vmqN3uQ7FjRGTy", "album"),
        ]

        for url, expected_type in test_cases:
            url_type = get_spotify_url_type(url)
            assert (
                url_type == expected_type
            ), f"Expected {expected_type}, got {url_type} for {url}"

    def test_get_spotify_url_type_invalid(self):
        """Test URL type detection for invalid URLs."""
        invalid_urls = ["invalid:url", "https://example.com", ""]

        for url in invalid_urls:
            url_type = get_spotify_url_type(url)
            assert url_type is None, f"Should return None for {url}, got {url_type}"

    def test_validate_spotify_url_edge_cases(self):
        """Test edge cases for URL validation."""
        edge_cases = [
            ("https://open.spotify.com/track/", True),  # Valid format even without ID
            ("spotify:track:", True),  # Valid format even without ID
            (
                "https://open.spotify.com/unknown/123",
                True,
            ),  # Unknown type but valid format
            ("spotify:unknown:123", True),  # Unknown type but valid format
        ]

        for url, expected_valid in edge_cases:
            is_valid, error = validate_spotify_url(url)
            assert (
                is_valid == expected_valid
            ), f"URL {url} should be {expected_valid}, got {is_valid}"

    def test_extract_spotify_id_edge_cases(self):
        """Test edge cases for ID extraction."""
        edge_cases = [
            ("https://open.spotify.com/track/", None),  # Missing ID
            ("spotify:track:", None),  # Missing ID
            (
                "https://open.spotify.com/unknown/123",
                "123",
            ),  # Unknown type but valid format
            ("spotify:unknown:123", "123"),  # Unknown type but valid format
        ]

        for url, expected_id in edge_cases:
            extracted_id = extract_spotify_id(url)
            assert (
                extracted_id == expected_id
            ), f"Expected {expected_id}, got {extracted_id} for {url}"

    def test_url_type_detection_case_insensitive(self):
        """Test that URL type detection is case insensitive."""
        test_cases = [
            ("https://open.spotify.com/TRACK/4iV5W9uYEdYUVa79Axb7Rh", "track"),
            ("https://open.spotify.com/ALBUM/4aawyAB9vmqN3uQ7FjRGTy", "album"),
            ("https://open.spotify.com/PLAYLIST/37i9dQZF1DXcBWIGoYBM5M", "playlist"),
            ("spotify:TRACK:4iV5W9uYEdYUVa79Axb7Rh", "track"),
            ("spotify:ALBUM:4aawyAB9vmqN3uQ7FjRGTy", "album"),
        ]

        for url, expected_type in test_cases:
            url_type = get_spotify_url_type(url)
            assert (
                url_type == expected_type
            ), f"Expected {expected_type}, got {url_type} for {url}"
