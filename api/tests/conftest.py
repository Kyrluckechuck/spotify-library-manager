"""Test configuration and fixtures."""

import os
import tempfile
from pathlib import Path

import django

import pytest

# Configure Django settings for testing
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_settings")
django.setup()


@pytest.fixture(autouse=True, scope="session")
def isolate_worker_directories(worker_id):
    """Isolate directories for each pytest-xdist worker to prevent race conditions."""
    if worker_id == "master":
        # Single-threaded execution, use base directories
        return

    # Get base directories from environment or use defaults
    base_tmpdir = os.environ.get("TMPDIR", tempfile.gettempdir())

    # Create unique directories for this worker
    worker_home = os.path.join(base_tmpdir, f"pytest-worker-{worker_id}-home")
    worker_tmpdir = os.path.join(base_tmpdir, f"pytest-worker-{worker_id}-tmp")
    worker_xdg_data = os.path.join(base_tmpdir, f"pytest-worker-{worker_id}-xdg-data")
    worker_xdg_cache = os.path.join(base_tmpdir, f"pytest-worker-{worker_id}-xdg-cache")
    worker_spotdl_cache = os.path.join(base_tmpdir, f"pytest-worker-{worker_id}-spotdl")

    # Create all worker directories
    for directory in [
        worker_home,
        worker_tmpdir,
        worker_xdg_data,
        worker_xdg_cache,
        worker_spotdl_cache,
    ]:
        Path(directory).mkdir(parents=True, exist_ok=True)

    # Set environment variables for this worker
    os.environ["HOME"] = worker_home
    os.environ["TMPDIR"] = worker_tmpdir
    os.environ["XDG_DATA_HOME"] = worker_xdg_data
    os.environ["XDG_CACHE_HOME"] = worker_xdg_cache
    os.environ["SPOTDL_CACHE_PATH"] = worker_spotdl_cache

    yield

    # Note: We don't clean up directories as they may contain useful debug info
    # and pytest-xdist will clean up temp directories after the session


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Automatically enable database access for all tests."""


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Set up the database for the test session."""
    with django_db_blocker.unblock():
        from django.core.management import call_command

        call_command("migrate", verbosity=0)


@pytest.fixture
def db_access_without_rollback_and_truncate(django_db_setup, django_db_blocker):
    """Provide database access without rollback and truncate."""
    django_db_blocker.unblock()
    yield
    django_db_blocker.restore()


# Test fixtures
@pytest.fixture
def sample_artist():
    """Create a sample artist for testing."""
    from library_manager.models import Artist

    return Artist.objects.create(name="Test Artist", gid="test123", tracked=True)


@pytest.fixture
def untracked_artist():
    """Create an untracked artist for testing."""
    from library_manager.models import Artist

    return Artist.objects.create(
        name="Untracked Artist", gid="untracked123", tracked=False
    )


@pytest.fixture
def multiple_artists():
    """Create multiple artists for testing pagination and filtering."""
    from library_manager.models import Artist

    artists = []
    for i in range(5):
        artist = Artist.objects.create(
            name=f"Artist {i}",
            gid=f"artist{i}",
            tracked=i % 2 == 0,  # Alternate tracked/untracked
        )
        artists.append(artist)
    return artists


@pytest.fixture
def sample_album(sample_artist):
    """Create a sample album for testing."""
    from library_manager.models import Album

    return Album.objects.create(
        name="Test Album",
        spotify_gid="album123",
        artist=sample_artist,
        total_tracks=10,
        wanted=True,
        downloaded=False,
    )


@pytest.fixture
def sample_song(sample_artist):
    """Create a sample artist for testing."""
    from library_manager.models import Song

    return Song.objects.create(
        name="Test Song",
        gid="song123",
        primary_artist=sample_artist,
        downloaded=False,
        unavailable=False,
    )


@pytest.fixture
def sample_playlist():
    """Create a sample playlist for testing."""
    from library_manager.models import TrackedPlaylist

    return TrackedPlaylist.objects.create(
        name="Test Playlist",
        url="https://open.spotify.com/playlist/test123",
        enabled=True,
        auto_track_artists=True,
    )
