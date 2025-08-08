"""Isolated integration tests with proper database handling."""

import pytest
from asgiref.sync import sync_to_async

from api.src.schema import schema


@pytest.mark.django_db
class TestIsolatedIntegration:
    """Test GraphQL integration with proper database isolation."""

    @pytest.mark.asyncio
    async def test_track_artist_mutation_isolated(self, transactional_db):
        """Test artist tracking with isolated database."""
        from library_manager.models import Artist

        # Create artist in isolated transaction
        artist = await sync_to_async(Artist.objects.create)(
            name="Test Artist", gid="test123", tracked=False
        )

        mutation = f"""
        mutation {{
            trackArtist(artistId: {artist.id}) {{
                success
                message
                artist {{
                    id
                    name
                    isTracked
                }}
            }}
        }}
        """

        result = await schema.execute(mutation)

        assert result.errors is None
        assert result.data is not None
        assert result.data["trackArtist"]["success"] is True
        assert result.data["trackArtist"]["artist"]["isTracked"] is True

        # Verify in database
        await sync_to_async(artist.refresh_from_db)()
        assert artist.tracked is True

    @pytest.mark.asyncio
    async def test_set_album_wanted_isolated(self, transactional_db):
        """Test album wanted setting with isolated database."""
        from library_manager.models import Album, Artist

        # Create artist and album in isolated transaction
        artist = await sync_to_async(Artist.objects.create)(
            name="Test Artist", gid="artist123", tracked=True
        )

        album = await sync_to_async(Album.objects.create)(
            name="Test Album",
            spotify_gid="album123",
            spotify_uri="spotify:album:album123",
            artist=artist,
            total_tracks=10,
            wanted=False,
            downloaded=False,
        )

        mutation = f"""
        mutation {{
            setAlbumWanted(albumId: {album.id}, wanted: true) {{
                success
                message
                album {{
                    id
                    name
                    wanted
                }}
            }}
        }}
        """

        result = await schema.execute(mutation)

        assert result.errors is None
        assert result.data is not None
        assert result.data["setAlbumWanted"]["success"] is True
        assert result.data["setAlbumWanted"]["album"]["wanted"] is True

        # Verify in database
        await sync_to_async(album.refresh_from_db)()
        assert album.wanted is True

    @pytest.mark.asyncio
    async def test_toggle_playlist_isolated(self, transactional_db):
        """Test playlist toggling with isolated database."""
        from library_manager.models import TrackedPlaylist

        # Create playlist in isolated transaction
        playlist = await sync_to_async(TrackedPlaylist.objects.create)(
            name="Test Playlist",
            url="https://open.spotify.com/playlist/test123",
            enabled=False,
            auto_track_artists=True,
        )

        mutation = f"""
        mutation {{
            togglePlaylist(playlistId: {playlist.id}) {{
                success
                message
                playlist {{
                    id
                    name
                    enabled
                }}
            }}
        }}
        """

        result = await schema.execute(mutation)

        assert result.errors is None
        assert result.data is not None
        assert result.data["togglePlaylist"]["success"] is True
        assert result.data["togglePlaylist"]["playlist"]["enabled"] is True

        # Verify in database
        await sync_to_async(playlist.refresh_from_db)()
        assert playlist.enabled is True

    @pytest.mark.asyncio
    async def test_artists_query_with_data_isolated(self, transactional_db):
        """Test artists query with isolated data."""
        from library_manager.models import Artist

        # Create artists in isolated transaction
        artists = []
        for i in range(3):
            artist = await sync_to_async(Artist.objects.create)(
                name=f"Artist {i}", gid=f"artist{i}", tracked=i % 2 == 0
            )
            artists.append(artist)

        query = """
        {
            artists(first: 10) {
                totalCount
                edges {
                    id
                    name
                    isTracked
                }
            }
        }
        """

        result = await schema.execute(query)

        assert result.errors is None
        assert result.data is not None
        assert result.data["artists"]["totalCount"] == 3
        assert len(result.data["artists"]["edges"]) == 3

    @pytest.mark.asyncio
    async def test_albums_query_with_data_isolated(self, transactional_db):
        """Test albums query with isolated data."""
        from library_manager.models import Album, Artist

        # Create artist and albums in isolated transaction
        artist = await sync_to_async(Artist.objects.create)(
            name="Test Artist", gid="artist123", tracked=True
        )

        albums = []
        for i in range(2):
            album = await sync_to_async(Album.objects.create)(
                name=f"Album {i}",
                spotify_gid=f"album{i}",
                spotify_uri=f"spotify:album:album{i}",
                artist=artist,
                total_tracks=10,
                wanted=True,
                downloaded=False,
            )
            albums.append(album)

        query = """
        {
            albums(first: 10) {
                totalCount
                edges {
                    id
                    name
                    wanted
                }
            }
        }
        """

        result = await schema.execute(query)

        assert result.errors is None
        assert result.data is not None
        assert result.data["albums"]["totalCount"] == 2
        assert len(result.data["albums"]["edges"]) == 2
