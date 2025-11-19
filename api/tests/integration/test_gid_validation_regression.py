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
    - Added validate_spotify_gid() function
    - Added validation in fetch_all_albums_for_artist task before using GID
    - Added model documentation and clean() validation
"""

from unittest.mock import patch

import pytest

from library_manager.models import Artist
from library_manager.tasks import fetch_all_albums_for_artist


@pytest.mark.django_db
class TestGidValidationRegression:
    """Regression tests for Spotify GID validation in tasks."""

    def test_fetch_all_albums_converts_hex_gid_to_spotify_id(self):
        """
        REGRESSION: Ensure 32-char hex GIDs are auto-converted to base62 Spotify IDs.

        This test prevents the bug where hex GIDs caused 400 errors from Spotify API.
        The system now gracefully converts hex GIDs to base62 format and updates the database.
        """
        # Create artist with 32-char hex GID (from production data)
        artist = Artist.objects.create(
            name="Test Artist with Hex GID",
            gid="85273dc1a556464e98d5faae420a5cbb",  # 32-char hex (legacy format)
            tracked=True,
        )

        # Mock the downloader to avoid actual API calls
        with patch(
            "downloader.downloader.Downloader.get_artist_albums"
        ) as mock_get_albums:
            mock_get_albums.return_value = []  # No albums to process

            # Fetch albums should succeed with auto-conversion
            try:
                fetch_all_albums_for_artist(artist.id)
            except Exception:
                # Task may fail due to download capability check, but GID should still be converted
                pass

            # Reload artist from database
            artist.refresh_from_db()

            # Verify GID was converted to base62 format
            assert len(artist.gid) == 22  # Base62 Spotify IDs are 22 chars
            assert artist.gid == "43fUAK2p4LkPWxTLXWvaBl"  # Converted value

    def test_fetch_all_albums_updates_album_fk_on_conversion(self):
        """
        REGRESSION: Verify albums' FK is updated when artist GID is converted.

        Album model has FK to Artist using to_field="gid", so when artist.gid changes,
        we must also update all albums' artist_gid column.
        """
        from library_manager.models import Album

        # Create artist with hex GID
        artist = Artist.objects.create(
            name="Test Artist with Albums",
            gid="92be5088b0b54882b1edd5b5cd439e48",  # 32-char hex
            tracked=True,
        )

        # Create albums that reference this artist's hex GID
        album1 = Album.objects.create(
            name="Test Album 1",
            spotify_gid="testalbum1234567890ab",
            artist=artist,
            spotify_uri="spotify:album:testalbum1234567890ab",
            total_tracks=10,
        )
        album2 = Album.objects.create(
            name="Test Album 2",
            spotify_gid="testalbum2234567890cd",
            artist=artist,
            spotify_uri="spotify:album:testalbum2234567890cd",
            total_tracks=12,
        )

        # Mock downloader
        with patch(
            "downloader.downloader.Downloader.get_artist_albums"
        ) as mock_get_albums:
            mock_get_albums.return_value = []

            # Fetch albums should convert GID and update FK
            try:
                fetch_all_albums_for_artist(artist.id)
            except Exception:
                pass

            # Reload from database
            artist.refresh_from_db()
            album1.refresh_from_db()
            album2.refresh_from_db()

            # Verify artist GID was converted to base62 format
            assert len(artist.gid) == 22  # Base62 Spotify IDs are 22 chars
            assert artist.gid == "4sTQVOfp9vEMCemLw50sbu"  # Converted from hex

            # Verify albums still reference the artist (FK was updated)
            assert album1.artist == artist
            assert album2.artist == artist

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

    def test_model_allows_hex_gid_for_migration(self):
        """
        Artist model should allow hex GIDs for backward compatibility during migration.

        Hex GIDs will be auto-converted to base62 when accessed by tasks/services.
        """
        artist = Artist(
            name="Test Artist",
            gid="85273dc1a556464e98d5faae420a5cbb",  # 32-char hex (legacy format)
        )

        # Should be able to create artist with hex GID
        artist.save()

        # Verify it was saved
        assert artist.id is not None
        assert artist.gid == "85273dc1a556464e98d5faae420a5cbb"

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
        ],
    )
    def test_various_invalid_gids_rejected(self, invalid_gid):
        """
        Test that truly invalid GIDs (not hex format) are rejected.

        Note: 32-char hex GIDs are now accepted for backward compatibility during migration.
        """
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
        # Should mention expected formats
        assert "22-character base62" in error_msg or "32-character hex" in error_msg


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
