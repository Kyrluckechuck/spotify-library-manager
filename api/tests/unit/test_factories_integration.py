"""Integration tests showing Factory Boy benefits."""

import pytest
from tests.factories import (
    AlbumFactory,
    ArtistFactory,
    DownloadedAlbumFactory,
    EnabledPlaylistFactory,
    SongFactory,
    TrackedArtistFactory,
    UntrackedArtistFactory,
    WantedAlbumFactory,
)

from src.services.album import AlbumService
from src.services.artist import ArtistService
from src.services.playlist import PlaylistService


@pytest.mark.django_db
class TestFactoryBoyIntegration:
    """Test how Factory Boy improves existing test code."""

    def test_artist_service_with_factories(self):
        """Test ArtistService using Factory Boy - much cleaner!"""
        # Before Factory Boy (tedious):
        # artist = Artist.objects.create(
        #     name="Test Artist",
        #     gid="test123",
        #     tracked=True,
        #     added_at=datetime.now(),
        #     last_synced_at=datetime.now()
        # )

        # With Factory Boy (clean):
        artist = ArtistFactory(tracked=True)

        service = ArtistService()
        result = service._to_graphql_type(artist)

        assert result.name == artist.name
        assert result.id == artist.id
        assert result.is_tracked == artist.tracked

    def test_album_service_with_factories(self):
        """Test AlbumService using Factory Boy - automatic relationships!"""
        # Before Factory Boy (complex):
        # artist = Artist.objects.create(name="Artist", gid="artist1", tracked=True)
        # album = Album.objects.create(
        #     name="Album",
        #     spotify_gid="album1",
        #     artist=artist,
        #     total_tracks=10,
        #     wanted=True,
        #     downloaded=False
        # )

        # With Factory Boy (simple):
        album = AlbumFactory(wanted=True, downloaded=False)

        service = AlbumService()
        result = service._to_graphql_type(album)

        assert result.name == album.name
        assert result.wanted == album.wanted
        assert result.downloaded == album.downloaded
        assert result.artist_id is not None  # Automatically created!

    def test_playlist_service_with_factories(self):
        """Test PlaylistService using Factory Boy."""
        playlist = EnabledPlaylistFactory()

        service = PlaylistService()
        result = service._to_graphql_type(playlist)

        assert result.name == playlist.name
        assert result.enabled == playlist.enabled

    def test_complex_scenario_with_factories(self):
        """Test complex scenarios with Factory Boy - relationships handled automatically."""
        # Create a tracked artist with multiple albums
        artist = TrackedArtistFactory()
        albums = AlbumFactory.create_batch(3, artist=artist, wanted=True)

        # Create songs for each album
        songs = []
        for album in albums:
            songs.extend(SongFactory.create_batch(5, primary_artist=artist))

        # Create enabled playlists
        playlists = EnabledPlaylistFactory.create_batch(2)

        # Test that everything is properly related
        assert len(albums) == 3
        assert len(songs) == 15
        assert len(playlists) == 2

        for album in albums:
            assert album.artist == artist
            assert album.wanted is True

        for song in songs:
            assert song.primary_artist == artist

        for playlist in playlists:
            assert playlist.enabled is True
            assert playlist.auto_track_artists is True

    def test_specialized_factories(self):
        """Test specialized factories for common scenarios."""
        # Tracked artist
        tracked_artist = TrackedArtistFactory()
        assert tracked_artist.tracked is True

        # Untracked artist
        untracked_artist = UntrackedArtistFactory()
        assert untracked_artist.tracked is False

        # Downloaded album
        downloaded_album = DownloadedAlbumFactory()
        assert downloaded_album.downloaded is True
        assert downloaded_album.wanted is True

        # Wanted but not downloaded album
        wanted_album = WantedAlbumFactory()
        assert wanted_album.downloaded is False
        assert wanted_album.wanted is True

        # Enabled playlist
        enabled_playlist = EnabledPlaylistFactory()
        assert enabled_playlist.enabled is True
        assert enabled_playlist.auto_track_artists is True

    def test_factory_with_custom_attributes(self):
        """Test factories with custom attributes - best of both worlds."""
        # Use factory for defaults, override specific fields
        artist = ArtistFactory(name="Custom Artist Name", tracked=True)

        assert artist.name == "Custom Artist Name"
        assert artist.tracked is True
        assert artist.gid.startswith("artist_")  # Factory handles this
        assert artist.added_at is not None  # Factory handles this too

    def test_batch_creation_performance(self):
        """Test batch creation performance with Factory Boy."""
        # Create 10 artists efficiently
        artists = ArtistFactory.create_batch(10)

        assert len(artists) == 10
        assert all(artist.name is not None for artist in artists)
        assert all(artist.gid.startswith("artist_") for artist in artists)

        # Create 5 albums with artists efficiently
        albums = AlbumFactory.create_batch(5)

        assert len(albums) == 5
        assert all(album.artist is not None for album in albums)
        assert all(album.name is not None for album in albums)

    def test_factory_uniqueness(self):
        """Test that factories create unique objects."""
        artist1 = ArtistFactory()
        artist2 = ArtistFactory()

        assert artist1.id != artist2.id
        assert artist1.gid != artist2.gid
        assert artist1.name != artist2.name  # Faker generates different names
