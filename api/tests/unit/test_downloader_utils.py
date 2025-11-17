"""Tests for downloader utility functions."""

import pytest
from downloader.utils import gid_to_uri, uri_to_gid


def test_uri_to_gid() -> None:
    """Test converting Spotify URI to internal GID format."""
    # Test with a known Spotify ID
    spotify_id = "4dSpK6RQ66rjinHJxA5P8s"
    result = uri_to_gid(spotify_id)

    # Should return a 32-character hex string
    assert isinstance(result, str)
    assert len(result) == 32
    # Hex strings should only contain 0-9, a-f
    assert all(c in "0123456789abcdef" for c in result)


def test_gid_to_uri() -> None:
    """Test converting internal GID to Spotify URI format."""
    # Create a hex GID
    hex_gid = "0000000000000000000000000000dead"

    result = gid_to_uri(hex_gid)

    # Should return a base62-encoded Spotify ID (22 chars)
    assert isinstance(result, str)
    assert len(result) == 22


def test_gid_uri_round_trip() -> None:
    """Test that converting URI->GID->URI preserves the value."""
    original_id = "4dSpK6RQ66rjinHJxA5P8s"

    # Convert to GID and back
    gid = uri_to_gid(original_id)
    restored_id = gid_to_uri(gid)

    # Should get back the original ID
    assert restored_id == original_id


def test_gid_to_uri_requires_hex_format() -> None:
    """Test that gid_to_uri correctly requires hex input, not Spotify IDs."""
    # This is the format that gid_to_uri expects (hex)
    hex_format = "00000000000000000000000000000001"

    # Should work without error
    result = gid_to_uri(hex_format)
    assert isinstance(result, str)

    # Spotify IDs (base62) should raise ValueError
    spotify_id = "4dSpK6RQ66rjinHJxA5P8s"
    with pytest.raises(ValueError, match="invalid literal for int"):
        gid_to_uri(spotify_id)
