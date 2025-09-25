"""Tests demonstrating Factory Boy usage."""

import pytest
from tests.factories import (
    AlbumFactory,
    ArtistFactory,
    DisabledPlaylistFactory,
    DownloadedAlbumFactory,
    EnabledPlaylistFactory,
    SongFactory,
    TrackedArtistFactory,
    TrackedPlaylistFactory,
    UntrackedArtistFactory,
    WantedAlbumFactory,
)


@pytest.mark.django_db
class TestFactoryBoyUsage:
    """Test Factory Boy factories for clean test data creation."""

    def test_artist_factory_creates_valid_artist(self):
        """Test that ArtistFactory creates valid artists."""
        artist = ArtistFactory()

        assert artist.name is not None
        assert len(artist.gid) == 32 and all(
            c in "0123456789abcdef" for c in artist.gid
        )
        assert isinstance(artist.tracked, bool)
        assert artist.added_at is not None

    def test_album_factory_creates_valid_album_with_artist(self):
        """Test that AlbumFactory creates albums with artists."""
        album = AlbumFactory()

        assert album.name is not None
        assert album.spotify_gid.startswith("album_")
        assert album.artist is not None
        assert album.artist.name is not None
        assert isinstance(album.downloaded, bool)
        assert isinstance(album.wanted, bool)

    def test_song_factory_creates_valid_song_with_artist(self):
        """Test that SongFactory creates songs with artists."""
        song = SongFactory()

        assert song.name is not None
        assert song.gid.startswith("song_")
        assert song.primary_artist is not None
        assert song.spotify_uri.startswith("spotify:track:")
        assert isinstance(song.downloaded, bool)

    def test_playlist_factory_creates_valid_playlist(self):
        """Test that TrackedPlaylistFactory creates valid playlists."""
        playlist = TrackedPlaylistFactory()

        assert playlist.name is not None
        assert playlist.url.startswith("https://open.spotify.com/playlist/")
        assert isinstance(playlist.enabled, bool)
        assert isinstance(playlist.auto_track_artists, bool)

    def test_tracked_artist_factory_creates_tracked_artist(self):
        """Test that TrackedArtistFactory creates tracked artists."""
        artist = TrackedArtistFactory()

        assert artist.tracked is True
        assert artist.name is not None

    def test_untracked_artist_factory_creates_untracked_artist(self):
        """Test that UntrackedArtistFactory creates untracked artists."""
        artist = UntrackedArtistFactory()

        assert artist.tracked is False
        assert artist.name is not None

    def test_downloaded_album_factory_creates_downloaded_album(self):
        """Test that DownloadedAlbumFactory creates downloaded albums."""
        album = DownloadedAlbumFactory()

        assert album.downloaded is True
        assert album.wanted is True
        assert album.artist is not None

    def test_wanted_album_factory_creates_wanted_album(self):
        """Test that WantedAlbumFactory creates wanted but not downloaded albums."""
        album = WantedAlbumFactory()

        assert album.downloaded is False
        assert album.wanted is True
        assert album.artist is not None

    def test_enabled_playlist_factory_creates_enabled_playlist(self):
        """Test that EnabledPlaylistFactory creates enabled playlists."""
        playlist = EnabledPlaylistFactory()

        assert playlist.enabled is True
        assert playlist.auto_track_artists is True

    def test_disabled_playlist_factory_creates_disabled_playlist(self):
        """Test that DisabledPlaylistFactory creates disabled playlists."""
        playlist = DisabledPlaylistFactory()

        assert playlist.enabled is False

    def test_multiple_artists_creation(self):
        """Test creating multiple artists efficiently."""
        artists = ArtistFactory.create_batch(5)

        assert len(artists) == 5
        for artist in artists:
            assert len(artist.gid) == 32 and all(
                c in "0123456789abcdef" for c in artist.gid
            )
            assert artist.name is not None

    def test_complex_relationship_creation(self):
        """Test creating complex relationships easily."""
        # Create an artist with multiple albums
        artist = ArtistFactory()
        albums = AlbumFactory.create_batch(3, artist=artist)

        assert len(albums) == 3
        for album in albums:
            assert album.artist == artist
            assert album.name is not None

    def test_factory_with_custom_attributes(self):
        """Test creating objects with custom attributes."""
        artist = ArtistFactory(name="Custom Artist", tracked=True)

        assert artist.name == "Custom Artist"
        assert artist.tracked is True
        assert len(artist.gid) == 32 and all(
            c in "0123456789abcdef" for c in artist.gid
        )  # Still uses factory for other fields

    def test_factory_creates_unique_objects(self):
        """Test that factories create unique objects."""
        artist1 = ArtistFactory()
        artist2 = ArtistFactory()

        assert artist1.id != artist2.id
        assert artist1.gid != artist2.gid
        assert artist1.name != artist2.name  # Faker generates different names
