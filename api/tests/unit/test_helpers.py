"""
Tests for helper functions in library_manager.helpers
"""

from unittest.mock import patch

from django.test import TestCase

from library_manager.helpers import (
    download_missing_tracked_artists,
    enqueue_artist_sync_with_download,
    enqueue_batch_artist_operations,
    enqueue_download_missing_albums_for_artists,
    enqueue_fetch_all_albums_for_artists,
    enqueue_priority_artist_operations,
    update_tracked_artists_albums,
)
from library_manager.models import Artist


class TestHelpers(TestCase):
    """Test helper functions for artist operations."""

    def setUp(self):
        """Set up test data."""
        self.artist1 = Artist.objects.create(
            name="Test Artist 1", gid="artist_123", tracked=True
        )
        self.artist2 = Artist.objects.create(
            name="Test Artist 2", gid="artist_456", tracked=True
        )
        self.artist3 = Artist.objects.create(
            name="Test Artist 3", gid="artist_789", tracked=False
        )

    @patch("library_manager.tasks.fetch_all_albums_for_artist")
    def test_enqueue_fetch_all_albums_for_artists_uses_database_ids(self, mock_fetch):
        """Test that enqueue_fetch_all_albums_for_artists uses database IDs."""
        artists = Artist.objects.filter(tracked=True)

        enqueue_fetch_all_albums_for_artists(artists)

        # Verify that fetch_all_albums_for_artist was called with database IDs
        expected_calls = [
            ((self.artist1.id,), {}),
            ((self.artist2.id,), {}),
        ]
        mock_fetch.assert_has_calls(expected_calls, any_order=True)
        assert mock_fetch.call_count == 2

    @patch("library_manager.tasks.download_missing_albums_for_artist")
    def test_enqueue_download_missing_albums_for_artists_uses_database_ids(
        self, mock_download
    ):
        """Test that enqueue_download_missing_albums_for_artists uses database IDs."""
        artists = Artist.objects.filter(tracked=True)

        enqueue_download_missing_albums_for_artists(artists)

        # Verify that download_missing_albums_for_artist was called with database IDs
        expected_calls = [
            ((self.artist1.id,), {}),
            ((self.artist2.id,), {}),
        ]
        mock_download.assert_has_calls(expected_calls, any_order=True)
        assert mock_download.call_count == 2

    @patch("library_manager.helpers.is_task_pending_or_running", return_value=False)
    @patch("library_manager.tasks.fetch_all_albums_for_artist")
    def test_update_tracked_artists_albums_uses_database_ids(
        self, mock_fetch, mock_is_pending
    ):
        """Test that update_tracked_artists_albums uses database IDs."""
        artists = [self.artist1, self.artist2]
        already_enqueued = []

        update_tracked_artists_albums(already_enqueued, artists)

        # Verify that apply_async was called with database IDs
        assert mock_fetch.apply_async.call_count == 2

        # Check that each call used the correct artist ID in args
        for call in mock_fetch.apply_async.call_args_list:
            args, kwargs = call
            assert "args" in kwargs
            assert len(kwargs["args"]) == 1
            assert kwargs["args"][0] in [self.artist1.id, self.artist2.id]
            # Verify task_id is set for deduplication
            assert "task_id" in kwargs

    @patch("library_manager.helpers.is_task_pending_or_running", return_value=False)
    @patch("library_manager.tasks.download_missing_albums_for_artist")
    def test_download_missing_tracked_artists_uses_database_ids(
        self, mock_download, mock_is_pending
    ):
        """Test that download_missing_tracked_artists uses database IDs."""
        artists = [self.artist1, self.artist2]
        already_enqueued = []

        download_missing_tracked_artists(already_enqueued, artists)

        # Verify that apply_async was called with database IDs
        assert mock_download.apply_async.call_count == 2

        # Check that each call used the correct artist ID and delay kwarg
        for call in mock_download.apply_async.call_args_list:
            args, kwargs = call
            assert "args" in kwargs
            assert len(kwargs["args"]) == 1
            assert kwargs["args"][0] in [self.artist1.id, self.artist2.id]
            # Verify delay kwarg is passed
            assert "kwargs" in kwargs
            assert kwargs["kwargs"] == {"delay": 5}
            # Verify task_id is set for deduplication
            assert "task_id" in kwargs

    @patch("library_manager.tasks.fetch_all_albums_for_artist")
    def test_enqueue_fetch_all_albums_for_artists_with_extra_args(self, mock_fetch):
        """Test that enqueue_fetch_all_albums_for_artists passes extra args correctly."""
        artists = Artist.objects.filter(tracked=True)
        extra_args = {"priority": 10}

        enqueue_fetch_all_albums_for_artists(artists, extra_args)

        # Verify that extra args are passed through
        expected_calls = [
            ((self.artist1.id,), extra_args),
            ((self.artist2.id,), extra_args),
        ]
        mock_fetch.assert_has_calls(expected_calls, any_order=True)

    @patch("library_manager.tasks.fetch_all_albums_for_artist")
    def test_enqueue_fetch_all_albums_for_artists_duplicate_prevention(
        self, mock_fetch
    ):
        """Test that enqueue_fetch_all_albums_for_artists prevents duplicates."""
        # Create a queryset with duplicate artists
        artists = Artist.objects.filter(tracked=True)

        enqueue_fetch_all_albums_for_artists(artists)

        # Should only call once per unique artist
        assert mock_fetch.call_count == 2
        # Verify unique database IDs were used
        called_ids = [call[0][0] for call in mock_fetch.call_args_list]
        assert len(set(called_ids)) == 2
        assert self.artist1.id in called_ids
        assert self.artist2.id in called_ids

    def test_artist_database_ids_are_integers(self):
        """Test that artist database IDs are integers (not gids)."""
        assert isinstance(self.artist1.id, int)
        assert isinstance(self.artist2.id, int)
        assert isinstance(self.artist3.id, int)

        # Verify gids are strings
        assert isinstance(self.artist1.gid, str)
        assert isinstance(self.artist2.gid, str)
        assert isinstance(self.artist3.gid, str)

        # Verify they're different
        assert self.artist1.id != self.artist1.gid
        assert self.artist2.id != self.artist2.gid
        assert self.artist3.id != self.artist3.gid

    @patch("library_manager.tasks.fetch_all_albums_for_artist")
    @patch("library_manager.tasks.download_missing_albums_for_artist")
    def test_enqueue_batch_artist_operations_uses_database_ids(
        self, mock_download, mock_fetch
    ):
        """Test that enqueue_batch_artist_operations uses database IDs."""
        artists = Artist.objects.filter(tracked=True)

        operation_counts = enqueue_batch_artist_operations(
            artists, operations=["fetch", "download"]
        )

        # Verify operations were called with database IDs
        expected_fetch_calls = [
            ((self.artist1.id,), {}),
            ((self.artist2.id,), {}),
        ]
        expected_download_calls = [
            ((self.artist1.id,), {}),
            ((self.artist2.id,), {}),
        ]

        mock_fetch.assert_has_calls(expected_fetch_calls, any_order=True)
        mock_download.assert_has_calls(expected_download_calls, any_order=True)

        # Verify operation counts
        assert operation_counts["fetch"] == 2
        assert operation_counts["download"] == 2

    @patch("library_manager.tasks.fetch_all_albums_for_artist")
    @patch("library_manager.tasks.download_missing_albums_for_artist")
    def test_enqueue_priority_artist_operations_with_limit(
        self, mock_download, mock_fetch
    ):
        """Test that enqueue_priority_artist_operations respects concurrency limits."""
        artists = Artist.objects.filter(tracked=True)

        operation_counts = enqueue_priority_artist_operations(artists, max_concurrent=1)

        # Should only process first artist due to concurrency limit
        assert mock_fetch.call_count == 1
        assert mock_download.call_count == 1

        # Verify operation counts
        assert operation_counts["fetch"] == 1
        assert operation_counts["download"] == 1

    @patch("library_manager.tasks.fetch_all_albums_for_artist")
    @patch("library_manager.tasks.download_missing_albums_for_artist")
    def test_enqueue_artist_sync_with_download_uses_database_ids(
        self, mock_download, mock_fetch
    ):
        """Test that enqueue_artist_sync_with_download uses database IDs."""
        artists = Artist.objects.filter(tracked=True)

        operation_counts = enqueue_artist_sync_with_download(
            artists, auto_download=True
        )

        # Verify operations were called with database IDs
        expected_fetch_calls = [
            ((self.artist1.id,), {"delay": 0}),
            ((self.artist2.id,), {"delay": 0}),
        ]
        expected_download_calls = [
            ((self.artist1.id,), {"delay": 0}),
            ((self.artist2.id,), {"delay": 0}),
        ]

        mock_fetch.assert_has_calls(expected_fetch_calls, any_order=True)
        mock_download.assert_has_calls(expected_download_calls, any_order=True)

        # Verify operation counts
        assert operation_counts["fetch"] == 2
        assert operation_counts["download"] == 2

    @patch("library_manager.tasks.fetch_all_albums_for_artist")
    def test_enqueue_artist_sync_without_download(self, mock_fetch):
        """Test that enqueue_artist_sync_with_download can skip downloads."""
        artists = Artist.objects.filter(tracked=True)

        operation_counts = enqueue_artist_sync_with_download(
            artists, auto_download=False
        )

        # Should only call fetch, not download
        assert mock_fetch.call_count == 2
        assert operation_counts["fetch"] == 2
        assert "download" not in operation_counts
