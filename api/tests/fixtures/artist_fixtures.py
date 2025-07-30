import pytest

from library_manager.models import Album, Artist, Song, TrackedPlaylist


@pytest.fixture
def sample_artist():
    """Create a sample artist for testing."""
    return Artist.objects.create(name="Test Artist", gid="test123", tracked=True)


@pytest.fixture
def untracked_artist():
    """Create an untracked artist for testing."""
    return Artist.objects.create(
        name="Untracked Artist", gid="untracked123", tracked=False
    )


@pytest.fixture
def multiple_artists():
    """Create multiple artists for testing pagination and filtering."""
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
    return Album.objects.create(
        name="Test Album",
        spotify_gid="album123",
        artist=sample_artist,
        total_tracks=10,
        wanted=True,
        downloaded=False,
    )


@pytest.fixture
def sample_song(sample_artist, sample_album):
    """Create a sample song for testing."""
    return Song.objects.create(
        name="Test Song",
        gid="song123",
        primary_artist=sample_artist,
        album=sample_album,
        downloaded=False,
        unavailable=False,
    )


@pytest.fixture
def sample_playlist():
    """Create a sample playlist for testing."""
    return TrackedPlaylist.objects.create(
        name="Test Playlist",
        url="https://open.spotify.com/playlist/test123",
        enabled=True,
        auto_track_artists=True,
    )
