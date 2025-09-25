"""Factory Boy factories for test data creation."""

from datetime import timezone

from factory import Faker, Sequence, SubFactory
from factory.django import DjangoModelFactory

from library_manager.models import (
    Album,
    Artist,
    DownloadHistory,
    Song,
    TaskHistory,
    TrackedPlaylist,
)


class ArtistFactory(DjangoModelFactory):
    """Factory for creating Artist instances."""

    class Meta:
        model = Artist

    name = Faker("name")
    gid = Sequence(lambda n: f"{n:032x}")  # Generate proper hexadecimal GIDs
    tracked = Faker("boolean")
    added_at = Faker("date_time", tzinfo=timezone.utc)
    last_synced_at = Faker("date_time", tzinfo=timezone.utc)


class AlbumFactory(DjangoModelFactory):
    """Factory for creating Album instances."""

    class Meta:
        model = Album

    name = Faker("sentence", nb_words=3)
    spotify_gid = Sequence(lambda n: f"album_{n}")
    spotify_uri = Sequence(lambda n: f"spotify:album:album_{n}")
    total_tracks = Faker("random_int", min=1, max=20)
    downloaded = Faker("boolean")
    wanted = Faker("boolean")
    album_type = Faker("random_element", elements=["album", "single", "compilation"])
    album_group = Faker("random_element", elements=["album", "single", "compilation"])
    artist = SubFactory(ArtistFactory)


class SongFactory(DjangoModelFactory):
    """Factory for creating Song instances."""

    class Meta:
        model = Song

    name = Faker("sentence", nb_words=4)
    gid = Sequence(lambda n: f"song_{n}")
    created_at = Faker("date_time", tzinfo=timezone.utc)
    failed_count = Faker("random_int", min=0, max=5)
    bitrate = Faker("random_int", min=128, max=320)
    unavailable = Faker("boolean")
    file_path = Faker("file_path")
    downloaded = Faker("boolean")
    primary_artist = SubFactory(ArtistFactory)


class TrackedPlaylistFactory(DjangoModelFactory):
    """Factory for creating TrackedPlaylist instances."""

    class Meta:
        model = TrackedPlaylist

    name = Faker("sentence", nb_words=3)
    url = Sequence(lambda n: f"https://open.spotify.com/playlist/playlist_{n}")
    enabled = Faker("boolean")
    auto_track_artists = Faker("boolean")
    last_synced_at = Faker("date_time", tzinfo=timezone.utc)


class TaskHistoryFactory(DjangoModelFactory):
    """Factory for creating TaskHistory instances."""

    class Meta:
        model = TaskHistory

    task_id = Sequence(lambda n: f"task_{n}")
    type = Faker("random_element", elements=["SYNC", "DOWNLOAD", "FETCH"])
    entity_id = Sequence(lambda n: f"entity_{n}")
    entity_type = Faker("random_element", elements=["ARTIST", "ALBUM", "PLAYLIST"])
    status = Faker(
        "random_element", elements=["RUNNING", "COMPLETED", "FAILED", "PENDING"]
    )
    started_at = Faker("date_time", tzinfo=timezone.utc)
    completed_at = Faker("date_time", tzinfo=timezone.utc)
    error_message = Faker("sentence")
    duration_seconds = Faker("random_int", min=1, max=3600)
    progress_percentage = Faker("random_int", min=0, max=100)
    log_messages = Faker("sentences", nb=3)


class DownloadHistoryFactory(DjangoModelFactory):
    """Factory for creating DownloadHistory instances."""

    class Meta:
        model = DownloadHistory

    url = Sequence(lambda n: f"spotify:track:download_{n}")
    added_at = Faker("date_time", tzinfo=timezone.utc)
    completed_at = Faker("date_time", tzinfo=timezone.utc)
    progress = Faker("random_int", min=0, max=100)
    error_message = Faker("sentence")


# Specialized factories for common test scenarios
class TrackedArtistFactory(ArtistFactory):
    """Factory for creating tracked artists."""

    tracked = True


class UntrackedArtistFactory(ArtistFactory):
    """Factory for creating untracked artists."""

    tracked = False


class DownloadedAlbumFactory(AlbumFactory):
    """Factory for creating downloaded albums."""

    downloaded = True
    wanted = True


class WantedAlbumFactory(AlbumFactory):
    """Factory for creating wanted but not downloaded albums."""

    downloaded = False
    wanted = True


class EnabledPlaylistFactory(TrackedPlaylistFactory):
    """Factory for creating enabled playlists."""

    enabled = True
    auto_track_artists = True


class DisabledPlaylistFactory(TrackedPlaylistFactory):
    """Factory for creating disabled playlists."""

    enabled = False


class CompletedTaskFactory(TaskHistoryFactory):
    """Factory for creating completed tasks."""

    status = "COMPLETED"
    completed_at = Faker("date_time", tzinfo=timezone.utc)
    duration_seconds = Faker("random_int", min=1, max=300)
    progress_percentage = 100


class FailedTaskFactory(TaskHistoryFactory):
    """Factory for creating failed tasks."""

    status = "FAILED"
    completed_at = Faker("date_time", tzinfo=timezone.utc)
    error_message = Faker("sentence")


class CompletedDownloadFactory(DownloadHistoryFactory):
    """Factory for creating completed downloads."""

    completed_at = Faker("date_time", tzinfo=timezone.utc)
    progress = 100
