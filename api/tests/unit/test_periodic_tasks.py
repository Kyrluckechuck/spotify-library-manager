"""
Tests for periodic Celery tasks in library_manager.tasks
"""

from unittest.mock import patch

from django.test import TestCase

from library_manager.models import (
    ALBUM_GROUPS_TO_IGNORE,
    ALBUM_TYPES_TO_DOWNLOAD,
    Album,
    Artist,
)


class TestPeriodicTasks(TestCase):
    """Test periodic Celery Beat tasks."""

    def setUp(self):
        """Set up test data."""
        # Create tracked artist with missing albums
        self.tracked_artist1 = Artist.objects.create(
            name="Tracked Artist 1", gid="tracked_123", tracked=True
        )
        self.tracked_artist2 = Artist.objects.create(
            name="Tracked Artist 2", gid="tracked_456", tracked=True
        )

        # Create untracked artist (should be ignored)
        self.untracked_artist = Artist.objects.create(
            name="Untracked Artist", gid="untracked_789", tracked=False
        )

        # Create albums for tracked artists
        # Missing albums (wanted=True, downloaded=False)
        self.missing_album1 = Album.objects.create(
            name="Missing Album 1",
            spotify_gid="album_001",
            spotify_uri="spotify:album:001",
            artist=self.tracked_artist1,
            wanted=True,
            downloaded=False,
            album_type="album",
            album_group="album",
            total_tracks=10,
        )
        self.missing_album2 = Album.objects.create(
            name="Missing Album 2",
            spotify_gid="album_002",
            spotify_uri="spotify:album:002",
            artist=self.tracked_artist2,
            wanted=True,
            downloaded=False,
            album_type="single",
            album_group="single",
            total_tracks=2,
        )

        # Already downloaded album (should be skipped)
        self.downloaded_album = Album.objects.create(
            name="Downloaded Album",
            spotify_gid="album_003",
            spotify_uri="spotify:album:003",
            artist=self.tracked_artist1,
            wanted=True,
            downloaded=True,
            album_type="album",
            album_group="album",
            total_tracks=12,
        )

        # Unwanted album (should be skipped)
        self.unwanted_album = Album.objects.create(
            name="Unwanted Album",
            spotify_gid="album_004",
            spotify_uri="spotify:album:004",
            artist=self.tracked_artist1,
            wanted=False,
            downloaded=False,
            album_type="album",
            album_group="album",
            total_tracks=8,
        )

        # "Appears on" album (should be excluded by album_group filter)
        self.appears_on_album = Album.objects.create(
            name="Appears On Album",
            spotify_gid="album_005",
            spotify_uri="spotify:album:005",
            artist=self.tracked_artist1,
            wanted=True,
            downloaded=False,
            album_type="compilation",
            album_group="appears_on",
            total_tracks=20,
        )

        # Album from untracked artist (should be skipped)
        self.untracked_album = Album.objects.create(
            name="Untracked Artist Album",
            spotify_gid="album_006",
            spotify_uri="spotify:album:006",
            artist=self.untracked_artist,
            wanted=True,
            downloaded=False,
            album_type="album",
            album_group="album",
            total_tracks=10,
        )

    @patch("library_manager.tasks.download_single_album")
    def test_queue_missing_albums_for_tracked_artists(self, mock_download):
        """Test that periodic task queues correct albums from tracked artists."""
        from library_manager.tasks import queue_missing_albums_for_tracked_artists

        # Run the periodic task
        queue_missing_albums_for_tracked_artists()

        # Verify download_single_album.delay() was called for correct albums only
        # Should queue: missing_album1, missing_album2
        # Should skip: downloaded_album (already downloaded),
        #              unwanted_album (wanted=False),
        #              appears_on_album (album_group excluded),
        #              untracked_album (artist not tracked)
        assert mock_download.delay.call_count == 2

        # Extract the album IDs that were queued
        queued_album_ids = [call[0][0] for call in mock_download.delay.call_args_list]

        # Verify correct albums were queued
        assert self.missing_album1.id in queued_album_ids
        assert self.missing_album2.id in queued_album_ids

        # Verify incorrect albums were NOT queued
        assert self.downloaded_album.id not in queued_album_ids
        assert self.unwanted_album.id not in queued_album_ids
        assert self.appears_on_album.id not in queued_album_ids
        assert self.untracked_album.id not in queued_album_ids

    @patch("library_manager.tasks.download_single_album")
    def test_queue_missing_albums_respects_300_limit(self, mock_download):
        """Test that periodic task respects the 300 album limit."""
        from library_manager.tasks import queue_missing_albums_for_tracked_artists

        # Create 350 missing albums to test the limit
        for i in range(350):
            Album.objects.create(
                name=f"Test Album {i}",
                spotify_gid=f"album_{i:04d}",
                spotify_uri=f"spotify:album:{i:04d}",
                artist=self.tracked_artist1,
                wanted=True,
                downloaded=False,
                album_type="album",
                album_group="album",
                total_tracks=10,
            )

        # Run the periodic task
        queue_missing_albums_for_tracked_artists()

        # Should only queue 300 albums (not all 352 = 350 + 2 from setUp)
        assert mock_download.delay.call_count == 300

    @patch("library_manager.tasks.download_single_album")
    def test_queue_missing_albums_handles_no_albums(self, mock_download):
        """Test that periodic task handles case when no albums need downloading."""
        from library_manager.tasks import queue_missing_albums_for_tracked_artists

        # Mark all albums as downloaded or unwanted
        Album.objects.filter(
            artist__tracked=True, wanted=True, downloaded=False
        ).update(downloaded=True)

        # Run the periodic task
        queue_missing_albums_for_tracked_artists()

        # Should not queue any albums
        assert mock_download.delay.call_count == 0

    @patch("library_manager.tasks.download_single_album")
    def test_queue_missing_albums_applies_album_type_filter(self, mock_download):
        """Test that periodic task only queues albums matching ALBUM_TYPES_TO_DOWNLOAD."""
        from library_manager.tasks import queue_missing_albums_for_tracked_artists

        # Create album with excluded type (assuming 'ep' is not in ALBUM_TYPES_TO_DOWNLOAD)
        excluded_type_album = Album.objects.create(
            name="EP Album",
            spotify_gid="album_ep",
            spotify_uri="spotify:album:ep",
            artist=self.tracked_artist1,
            wanted=True,
            downloaded=False,
            album_type="ep",  # Assuming 'ep' is not in ALBUM_TYPES_TO_DOWNLOAD
            album_group="album",
            total_tracks=6,
        )

        # Run the periodic task
        queue_missing_albums_for_tracked_artists()

        # Verify EP was not queued if 'ep' not in ALBUM_TYPES_TO_DOWNLOAD
        queued_album_ids = [call[0][0] for call in mock_download.delay.call_args_list]

        if "ep" not in ALBUM_TYPES_TO_DOWNLOAD:
            assert excluded_type_album.id not in queued_album_ids

    @patch("library_manager.tasks.download_single_album")
    def test_queue_missing_albums_excludes_album_groups(self, mock_download):
        """Test that periodic task excludes albums from ALBUM_GROUPS_TO_IGNORE."""
        from library_manager.tasks import queue_missing_albums_for_tracked_artists

        # Run the periodic task
        queue_missing_albums_for_tracked_artists()

        # Verify appears_on album was excluded
        queued_album_ids = [call[0][0] for call in mock_download.delay.call_args_list]
        assert self.appears_on_album.id not in queued_album_ids

        # Verify the constant is configured as expected
        assert "appears_on" in ALBUM_GROUPS_TO_IGNORE

    @patch("library_manager.tasks.download_single_album")
    def test_queue_missing_albums_handles_task_queue_failure(self, mock_download):
        """Test that periodic task continues even if individual album queuing fails."""
        from library_manager.tasks import queue_missing_albums_for_tracked_artists

        # Make delay() raise an exception on first call, succeed on second
        mock_download.delay.side_effect = [Exception("Queue error"), None]

        # Run the periodic task - should not crash
        queue_missing_albums_for_tracked_artists()

        # Should have attempted to queue both albums despite first failure
        assert mock_download.delay.call_count == 2
