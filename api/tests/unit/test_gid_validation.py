"""
Unit tests for Spotify GID validation.

These tests ensure that invalid Spotify IDs are caught before making API calls,
preventing 400 "Invalid base62 id" errors from the Spotify API.
"""

import pytest

from library_manager.validators import (
    extract_spotify_id_from_uri,
    is_valid_spotify_id,
    validate_spotify_gid,
)


class TestIsValidSpotifyId:
    """Test Spotify ID format validation."""

    def test_valid_spotify_ids(self):
        """Valid 22-character base62 Spotify IDs should pass."""
        valid_ids = [
            "4iV5W9uYEdYUVa79Axb7Rh",  # Artist
            "7K3BhSpAxZBzniskgIPUYj",  # Album
            "6rqhFgbbKwnb9MLmUQDhG6",  # Track
            "4dSpK6RQ66rjinHJxA5P8s",  # Real artist from DB
            "0123456789ABCDEFGHabcd",  # All valid base62 chars
        ]
        for spotify_id in valid_ids:
            assert is_valid_spotify_id(spotify_id), f"Should be valid: {spotify_id}"

    def test_invalid_32char_hex_uuid(self):
        """32-character hex UUIDs should be rejected."""
        invalid_ids = [
            "85273dc1a556464e98d5faae420a5cbb",  # From production bug
            "353bfdb3251247dfab0b798706e2db2a",  # From production bug
            "6a0d178af7434be899693e738fc40dd9",  # From production bug
            "4e7a5a3185bc404abeaf1c8462586d2f",  # From error logs
        ]
        for spotify_id in invalid_ids:
            assert not is_valid_spotify_id(
                spotify_id
            ), f"Should be invalid: {spotify_id}"

    def test_invalid_lengths(self):
        """IDs with incorrect length should be rejected."""
        assert not is_valid_spotify_id("too_short")
        assert not is_valid_spotify_id("way_too_long_to_be_a_spotify_id_string")
        assert not is_valid_spotify_id("")
        assert not is_valid_spotify_id("4iV5W9uYEdYUVa79Axb7R")  # 21 chars
        assert not is_valid_spotify_id("4iV5W9uYEdYUVa79Axb7Rh1")  # 23 chars

    def test_invalid_characters(self):
        """IDs with non-alphanumeric chars should be rejected."""
        assert not is_valid_spotify_id("4iV5W9uYEdYUVa79Axb7R-")  # Hyphen
        assert not is_valid_spotify_id("4iV5W9uYEdYUVa79Axb7R_")  # Underscore
        assert not is_valid_spotify_id("4iV5W9uYEdYUVa79Axb7R ")  # Space
        assert not is_valid_spotify_id("4iV5W9uYEdYUVa79Axb7R!")  # Special char

    def test_none_and_non_string(self):
        """None and non-string inputs should be rejected."""
        assert not is_valid_spotify_id(None)
        assert not is_valid_spotify_id(123)
        assert not is_valid_spotify_id([])
        assert not is_valid_spotify_id({})


class TestExtractSpotifyIdFromUri:
    """Test Spotify ID extraction from URIs and URLs."""

    def test_extract_from_spotify_uri(self):
        """Should extract ID from spotify: URI format."""
        assert (
            extract_spotify_id_from_uri("spotify:artist:4iV5W9uYEdYUVa79Axb7Rh")
            == "4iV5W9uYEdYUVa79Axb7Rh"
        )
        assert (
            extract_spotify_id_from_uri("spotify:album:7K3BhSpAxZBzniskgIPUYj")
            == "7K3BhSpAxZBzniskgIPUYj"
        )
        assert (
            extract_spotify_id_from_uri("spotify:track:6rqhFgbbKwnb9MLmUQDhG6")
            == "6rqhFgbbKwnb9MLmUQDhG6"
        )

    def test_extract_from_spotify_url(self):
        """Should extract ID from open.spotify.com URLs."""
        assert (
            extract_spotify_id_from_uri(
                "https://open.spotify.com/artist/4iV5W9uYEdYUVa79Axb7Rh"
            )
            == "4iV5W9uYEdYUVa79Axb7Rh"
        )
        assert (
            extract_spotify_id_from_uri(
                "https://open.spotify.com/album/7K3BhSpAxZBzniskgIPUYj?si=abc123"
            )
            == "7K3BhSpAxZBzniskgIPUYj"
        )

    def test_extract_from_bare_id(self):
        """Should return valid bare IDs as-is."""
        assert (
            extract_spotify_id_from_uri("4iV5W9uYEdYUVa79Axb7Rh")
            == "4iV5W9uYEdYUVa79Axb7Rh"
        )

    def test_invalid_uris_return_none(self):
        """Invalid URIs should return None."""
        assert extract_spotify_id_from_uri("") is None
        assert extract_spotify_id_from_uri("invalid") is None
        assert extract_spotify_id_from_uri("85273dc1a556464e98d5faae420a5cbb") is None
        assert extract_spotify_id_from_uri(None) is None


class TestValidateSpotifyGid:
    """Test GID validation that raises descriptive errors."""

    def test_valid_gid_passes(self):
        """Valid GIDs should not raise errors."""
        validate_spotify_gid("4iV5W9uYEdYUVa79Axb7Rh", "artist")
        validate_spotify_gid("7K3BhSpAxZBzniskgIPUYj", "album")
        # Should complete without exception

    def test_empty_gid_raises_error(self):
        """Empty GID should raise ValueError."""
        with pytest.raises(ValueError, match="Missing Spotify artist GID"):
            validate_spotify_gid("", "artist")

        with pytest.raises(ValueError, match="Missing Spotify album GID"):
            validate_spotify_gid(None, "album")

    def test_32char_hex_uuid_raises_descriptive_error(self):
        """
        32-char hex GID should raise error with conversion suggestion.

        Note: validate_spotify_gid() is deprecated. Use normalize_spotify_gid() instead
        for automatic conversion.
        """
        with pytest.raises(ValueError) as exc_info:
            validate_spotify_gid("85273dc1a556464e98d5faae420a5cbb", "artist")

        error_msg = str(exc_info.value)
        assert "Invalid Spotify artist GID" in error_msg
        assert "32-character string" in error_msg
        assert "legacy hex-encoded GID" in error_msg
        assert "normalize_spotify_gid()" in error_msg

    def test_wrong_length_raises_descriptive_error(self):
        """IDs with wrong length should raise error with helpful context."""
        # Too short
        with pytest.raises(ValueError) as exc_info:
            validate_spotify_gid("tooshort", "artist")
        assert "too short" in str(exc_info.value).lower()

        # Too long
        with pytest.raises(ValueError) as exc_info:
            validate_spotify_gid("waytoolongtobeaspotifyid123", "artist")
        assert "too long" in str(exc_info.value).lower()

    def test_invalid_chars_raises_descriptive_error(self):
        """IDs with invalid characters should raise error."""
        with pytest.raises(ValueError) as exc_info:
            validate_spotify_gid("4iV5W9uYEdYUVa79Axb7R-", "artist")
        assert "invalid characters" in str(exc_info.value).lower()
