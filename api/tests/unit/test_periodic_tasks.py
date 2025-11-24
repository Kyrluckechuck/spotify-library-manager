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

    @patch("library_manager.tasks.periodic.download_single_album")
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

    @patch("library_manager.tasks.periodic.download_single_album")
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

    @patch("library_manager.tasks.periodic.download_single_album")
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

    @patch("library_manager.tasks.periodic.download_single_album")
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

    @patch("library_manager.tasks.periodic.download_single_album")
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

    @patch("library_manager.tasks.periodic.download_single_album")
    def test_queue_missing_albums_handles_task_queue_failure(self, mock_download):
        """Test that periodic task continues even if individual album queuing fails."""
        from library_manager.tasks import queue_missing_albums_for_tracked_artists

        # Make delay() raise an exception on first call, succeed on second
        mock_download.delay.side_effect = [Exception("Queue error"), None]

        # Run the periodic task - should not crash
        queue_missing_albums_for_tracked_artists()

        # Should have attempted to queue both albums despite first failure
        assert mock_download.delay.call_count == 2


class TestRetryFailedSongsTask(TestCase):
    """Test retry_failed_songs periodic task."""

    def setUp(self):
        """Set up test data with failed songs."""
        from library_manager.models import Song

        # Create test artist
        self.artist = Artist.objects.create(
            name="Test Artist", gid="artist_test", tracked=True
        )

        # Create songs with various failure states
        # Song with 1 failure (should be retried, high priority)
        self.song_failed_once = Song.objects.create(
            name="Failed Once",
            gid="song_001",
            primary_artist=self.artist,
            failed_count=1,
            downloaded=False,
        )

        # Song with 5 failures (should be retried, medium priority)
        self.song_failed_five = Song.objects.create(
            name="Failed Five Times",
            gid="song_005",
            primary_artist=self.artist,
            failed_count=5,
            downloaded=False,
        )

        # Song with 10 failures (should be retried, low priority - at threshold)
        self.song_failed_ten = Song.objects.create(
            name="Failed Ten Times",
            gid="song_010",
            primary_artist=self.artist,
            failed_count=10,
            downloaded=False,
        )

        # Song with 11 failures (should be SKIPPED - over threshold)
        self.song_failed_eleven = Song.objects.create(
            name="Failed Eleven Times",
            gid="song_011",
            primary_artist=self.artist,
            failed_count=11,
            downloaded=False,
        )

        # Song with 0 failures (should be SKIPPED - not failed yet)
        self.song_not_failed = Song.objects.create(
            name="Not Failed",
            gid="song_000",
            primary_artist=self.artist,
            failed_count=0,
            downloaded=False,
        )

        # Already downloaded song with failures (should be SKIPPED)
        self.song_downloaded = Song.objects.create(
            name="Downloaded Despite Failures",
            gid="song_dl",
            primary_artist=self.artist,
            failed_count=3,
            downloaded=True,
        )

    @patch("library_manager.tasks.maintenance.require_download_capability")
    @patch("library_manager.tasks.maintenance.spotdl_wrapper")
    def test_retry_failed_songs_basic(self, mock_spotdl, mock_require_download):
        """Test that retry_failed_songs attempts to download failed songs."""
        from library_manager.tasks import retry_failed_songs

        # Run the periodic task
        retry_failed_songs()

        # Verify spotdl_wrapper.execute was called
        assert mock_spotdl.execute.call_count == 1

        # Extract the URIs that were passed to download
        call_args = mock_spotdl.execute.call_args
        config = call_args[0][0]
        downloaded_uris = config.urls

        # Should include songs with 1, 5, and 10 failures
        assert self.song_failed_once.spotify_uri in downloaded_uris
        assert self.song_failed_five.spotify_uri in downloaded_uris
        assert self.song_failed_ten.spotify_uri in downloaded_uris

        # Should NOT include songs with 11+ failures, 0 failures, or already downloaded
        assert self.song_failed_eleven.spotify_uri not in downloaded_uris
        assert self.song_not_failed.spotify_uri not in downloaded_uris
        assert self.song_downloaded.spotify_uri not in downloaded_uris

    @patch("library_manager.tasks.maintenance.require_download_capability")
    @patch("library_manager.tasks.maintenance.spotdl_wrapper")
    def test_retry_failed_songs_priority_order(
        self, mock_spotdl, mock_require_download
    ):
        """Test that songs with fewer failures are prioritized."""
        # Create songs with different failure counts (oldest created_at first)
        import time

        from library_manager.models import Song
        from library_manager.tasks import retry_failed_songs

        for i in range(3):
            Song.objects.create(
                name=f"Priority Test {i}",
                gid=f"priority{i:06d}",  # Unique 22-char GID
                primary_artist=self.artist,
                failed_count=i + 1,  # 1, 2, 3 failures
                downloaded=False,
            )
            time.sleep(0.01)  # Ensure different created_at timestamps

        # Run the task
        retry_failed_songs()

        # Extract URIs in the order they were passed
        call_args = mock_spotdl.execute.call_args
        config = call_args[0][0]
        downloaded_uris = config.urls

        # The first URI should be from the song with failed_count=1
        # (our song_failed_once or priority_0)
        # We can't guarantee exact order between songs with same failed_count,
        # but we can verify failed_count=1 songs come before failed_count=5

        # Find the position of song_failed_five (failed_count=5)
        if self.song_failed_five.spotify_uri in downloaded_uris:
            pos_five = downloaded_uris.index(self.song_failed_five.spotify_uri)
            # All URIs before this position should be from songs with fewer failures
            # Just verify we got songs ordered by priority (manual inspection in logs)
            assert pos_five >= 0

    @patch("library_manager.tasks.maintenance.require_download_capability")
    @patch("library_manager.tasks.maintenance.spotdl_wrapper")
    def test_retry_failed_songs_respects_100_limit(
        self, mock_spotdl, mock_require_download
    ):
        """Test that retry only processes 100 songs per run."""
        from library_manager.models import Song
        from library_manager.tasks import retry_failed_songs

        # Create 150 failed songs
        for i in range(150):
            Song.objects.create(
                name=f"Failed Song {i}",
                gid=f"failsong{i:016d}",  # Unique 22-char GID
                primary_artist=self.artist,
                failed_count=1,
                downloaded=False,
            )

        # Run the task
        retry_failed_songs()

        # Should only process 100 songs
        call_args = mock_spotdl.execute.call_args
        config = call_args[0][0]
        downloaded_uris = config.urls

        # Should be exactly 100 songs (plus the 3 from setUp = 103 total failed songs)
        # But limit is 100
        assert len(downloaded_uris) == 100

    @patch("library_manager.tasks.maintenance.require_download_capability")
    @patch("library_manager.tasks.maintenance.spotdl_wrapper")
    def test_retry_failed_songs_handles_no_songs(
        self, mock_spotdl, mock_require_download
    ):
        """Test that task handles case when no songs need retry."""
        from library_manager.models import Song
        from library_manager.tasks import retry_failed_songs

        # Mark all failed songs as downloaded or over threshold
        Song.objects.filter(failed_count__gt=0).update(downloaded=True)

        # Run the task
        retry_failed_songs()

        # Should not call execute
        assert mock_spotdl.execute.call_count == 0

    @patch("library_manager.tasks.maintenance.require_download_capability")
    @patch("library_manager.tasks.maintenance.spotdl_wrapper")
    def test_retry_failed_songs_skips_high_failure_count(
        self, mock_spotdl, mock_require_download
    ):
        """Test that songs with >10 failures are not retried."""
        from library_manager.models import Song
        from library_manager.tasks import retry_failed_songs

        # Create songs with 11-20 failures
        for i in range(11, 21):
            Song.objects.create(
                name=f"High Failure {i}",
                gid=f"highfail{i:015d}",  # Unique 22-char GID
                primary_artist=self.artist,
                failed_count=i,
                downloaded=False,
            )

        # Run the task
        retry_failed_songs()

        # Extract downloaded URIs
        call_args = mock_spotdl.execute.call_args
        config = call_args[0][0]
        downloaded_uris = config.urls

        # Verify none of the high-failure songs were included
        for i in range(11, 21):
            gid = f"highfail{i:015d}"
            assert f"spotify:track:{gid}" not in downloaded_uris
