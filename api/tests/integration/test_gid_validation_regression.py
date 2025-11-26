"""
Regression tests for GID validation in tasks.

This test suite prevents the regression where invalid Spotify GIDs (32-char hex UUIDs)
were being passed to the Spotify API, causing 400 "Invalid base62 id" errors.

Production Error:
    HTTP Error for GET to https://api.spotify.com/v1/artists/4e7a5a3185bc404abeaf1c8462586d2f/albums
    returned 400 due to Invalid base62 id

Root Cause:
    Artist.gid field contained 32-character hex UUIDs instead of 22-character Spotify IDs,
    and fetch_all_albums_for_artist task was using artist.gid without validation.

Fix:
    - Database migration 0015_normalize_gids.py converts all hex GIDs to base62 format
    - Added validate_spotify_gid() function for validation
    - Added model clean() validation that rejects non-base62 GIDs
"""

from unittest.mock import patch

import pytest

from library_manager.models import Artist
from library_manager.tasks import fetch_all_albums_for_artist


@pytest.mark.django_db
class TestGidValidationRegression:
    """Regression tests for Spotify GID validation in tasks."""

    def test_fetch_all_albums_accepts_valid_spotify_id(self):
        """Valid 22-char Spotify IDs should be accepted."""
        artist = Artist.objects.create(
            name="Valid Artist",
            gid="4iV5W9uYEdYUVa79Axb7Rh",  # Valid 22-char Spotify ID
            tracked=True,
        )

        # Mock the downloader to avoid actual API calls
        with patch(
            "downloader.downloader.Downloader.get_artist_albums"
        ) as mock_get_albums:
            mock_get_albums.return_value = []  # No albums to process

            # Should not raise ValueError - validation passes
            try:
                fetch_all_albums_for_artist(artist.id)
            except ValueError as e:
                if "Invalid Spotify" in str(e):
                    pytest.fail(f"Valid Spotify ID was rejected: {e}")
            except Exception:
                # Task may fail for other reasons (download capability), but not GID validation
                pass

            # Verify GID was not changed (already valid base62)
            artist.refresh_from_db()
            assert artist.gid == "4iV5W9uYEdYUVa79Axb7Rh"

    def test_model_rejects_hex_gid(self):
        """
        Artist model should reject hex GIDs now that migration is complete.

        Migration 0015_normalize_gids converted all hex GIDs to base62 format,
        so we no longer need to accept hex GIDs.
        """
        artist = Artist(
            name="Test Artist",
            gid="85273dc1a556464e98d5faae420a5cbb",  # 32-char hex (legacy format)
        )

        # clean() should reject hex GID
        with pytest.raises(ValueError) as exc_info:
            artist.clean()

        assert "Invalid Spotify artist GID" in str(exc_info.value)

    def test_model_clean_validation_accepts_valid_gid(self):
        """Artist.clean() should accept valid Spotify IDs."""
        artist = Artist(
            name="Valid Artist",
            gid="4iV5W9uYEdYUVa79Axb7Rh",  # Valid 22-char Spotify ID
        )

        # Should not raise exception
        artist.clean()  # Only validate model logic, not field constraints

    @pytest.mark.parametrize(
        "invalid_gid",
        [
            "tooshort",  # Too short
            "waytoolongtobeaspotifyidstring",  # Wrong length (30 chars)
            "4iV5W9uYEdYUVa79Axb7R-",  # Invalid characters (has dash)
            "85273dc1a556464e98d5faae420a5cbb",  # 32-char hex (no longer allowed)
        ],
    )
    def test_various_invalid_gids_rejected(self, invalid_gid):
        """Test that invalid GIDs are rejected by model validation."""
        artist = Artist.objects.create(
            name="Test Artist",
            gid="4iV5W9uYEdYUVa79Axb7Rh",  # Start with valid, then update
            tracked=True,
        )

        # Update to invalid GID
        artist.gid = invalid_gid

        # Calling clean() should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            artist.clean()

        error_msg = str(exc_info.value)
        assert "Invalid Spotify artist GID" in error_msg
        assert "22-character base62" in error_msg


@pytest.mark.django_db
class TestGidDataQuality:
    """Tests to ensure GID data quality is maintained."""

    def test_no_32char_hex_gids_in_production(self):
        """
        Data quality check: Ensure no 32-char hex UUIDs exist in Artist.gid field.

        This test will fail if invalid GIDs are present, alerting to data quality issues.
        """
        import re

        # Find all artists with 32-char hex GIDs
        artists = Artist.objects.all()
        invalid_artists = []

        for artist in artists:
            if len(artist.gid) == 32 and re.match(r"^[a-f0-9]{32}$", artist.gid):
                invalid_artists.append((artist.id, artist.name, artist.gid))

        # Log details if invalid artists found
        if invalid_artists:
            details = "\n".join(
                [
                    f"  - ID {id}: {name} (GID: {gid})"
                    for id, name, gid in invalid_artists
                ]
            )
            pytest.fail(
                f"Found {len(invalid_artists)} artists with invalid 32-char hex GIDs:\n{details}\n\n"
                f"These artists need their GID field updated with valid Spotify IDs."
            )

    def test_all_artist_gids_are_valid_spotify_ids(self):
        """
        Data quality check: Ensure all Artist GIDs are valid 22-char Spotify IDs.

        This comprehensive check validates all GID data in the database.
        """
        from library_manager.validators import is_valid_spotify_id

        artists = Artist.objects.all()
        invalid_artists = []

        for artist in artists:
            if not is_valid_spotify_id(artist.gid):
                invalid_artists.append(
                    (artist.id, artist.name, artist.gid, len(artist.gid))
                )

        # Log details if invalid artists found
        if invalid_artists:
            details = "\n".join(
                [
                    f"  - ID {id}: {name} (GID: {gid}, len: {length})"
                    for id, name, gid, length in invalid_artists
                ]
            )
            pytest.fail(
                f"Found {len(invalid_artists)} artists with invalid Spotify IDs:\n{details}\n\n"
                f"All artists must have valid 22-character Spotify IDs in the gid field."
            )
