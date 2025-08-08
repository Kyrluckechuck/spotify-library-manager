"""Integration tests for GraphQL queries."""

from django.test import TransactionTestCase

from asgiref.sync import sync_to_async

from api.src.schema import schema
from library_manager.models import Album, Artist


class TestArtistQueries(TransactionTestCase):
    """Test artist-related queries."""

    async def test_artists_query_with_data(self):
        """Test artists query with data."""
        # Create test data
        await sync_to_async(Artist.objects.create)(
            name="Test Artist", gid="test123", tracked=True
        )

        query = """
        query Artists {
            artists {
                edges {
                    id
                    name
                    isTracked
                }
                totalCount
            }
        }
        """

        result = await schema.execute(query)

        assert result.errors is None
        assert result.data["artists"]["totalCount"] >= 1
        assert len(result.data["artists"]["edges"]) >= 1

    async def test_artists_query_with_filter(self):
        """Test artists query with filtering."""
        # Create test data
        await sync_to_async(Artist.objects.create)(
            name="Tracked Artist", gid="tracked123", tracked=True
        )
        await sync_to_async(Artist.objects.create)(
            name="Untracked Artist", gid="untracked123", tracked=False
        )

        query = """
        query Artists($isTracked: Boolean) {
            artists(isTracked: $isTracked) {
                edges {
                    id
                    name
                    isTracked
                }
                totalCount
            }
        }
        """

        variables = {"isTracked": True}
        result = await schema.execute(query, variable_values=variables)

        assert result.errors is None
        # Should only return tracked artists
        for artist in result.data["artists"]["edges"]:
            assert artist["isTracked"] is True

    async def test_artists_query_with_pagination(self):
        """Test artists query with pagination."""
        # Create test data
        for i in range(3):
            await sync_to_async(Artist.objects.create)(
                name=f"Artist {i}", gid=f"artist{i}", tracked=True
            )

        query = """
        query Artists($first: Int) {
            artists(first: $first) {
                edges {
                    id
                    name
                }
                pageInfo {
                    hasNextPage
                    hasPreviousPage
                }
                totalCount
            }
        }
        """

        variables = {"first": 1}
        result = await schema.execute(query, variable_values=variables)

        assert result.errors is None
        assert len(result.data["artists"]["edges"]) <= 1
        assert result.data["artists"]["totalCount"] >= 1

    async def test_artists_query_with_search(self):
        """Test artists query with search."""
        # Create test data
        await sync_to_async(Artist.objects.create)(
            name="Zebra Artist", gid="zebra123", tracked=True
        )
        await sync_to_async(Artist.objects.create)(
            name="Alpha Artist", gid="alpha123", tracked=True
        )

        query = """
        query Artists($search: String) {
            artists(search: $search) {
                edges {
                    id
                    name
                }
                totalCount
            }
        }
        """

        variables = {"search": "Zebra"}
        result = await schema.execute(query, variable_values=variables)

        assert result.errors is None
        assert result.data["artists"]["totalCount"] >= 1


class TestAlbumQueries(TransactionTestCase):
    """Test album-related queries."""

    async def test_albums_query(self):
        """Test albums query."""
        # Create test data
        artist = await sync_to_async(Artist.objects.create)(
            name="Test Artist", gid="test123", tracked=True
        )
        await sync_to_async(Album.objects.create)(
            name="Test Album",
            spotify_gid="album123",
            artist=artist,
            total_tracks=10,
            wanted=True,
            downloaded=False,
        )

        query = """
        query Albums {
            albums {
                edges {
                    id
                    name
                    wanted
                    downloaded
                }
                totalCount
            }
        }
        """

        result = await schema.execute(query)

        assert result.errors is None
        assert result.data["albums"]["totalCount"] >= 1
        assert len(result.data["albums"]["edges"]) >= 1


class TestArtistMutations(TransactionTestCase):
    """Test artist-related mutations."""

    async def test_track_artist_mutation(self):
        """Test artist tracking mutation."""
        # Create test data
        untracked_artist = await sync_to_async(Artist.objects.create)(
            name="Untracked Artist", gid="untracked123", tracked=False
        )

        mutation = """
        mutation TrackArtist($artistId: Int!) {
            trackArtist(artistId: $artistId) {
                success
                message
                artist {
                    id
                    name
                    isTracked
                }
            }
        }
        """

        variables = {"artistId": untracked_artist.id}
        result = await schema.execute(mutation, variable_values=variables)

        assert result.errors is None
        assert result.data["trackArtist"]["success"] is True
        assert result.data["trackArtist"]["artist"]["isTracked"] is True

    async def test_track_nonexistent_artist(self):
        """Test tracking non-existent artist."""
        mutation = """
        mutation TrackArtist($artistId: Int!) {
            trackArtist(artistId: $artistId) {
                success
                message
                artist {
                    id
                    name
                    isTracked
                }
            }
        }
        """

        variables = {"artistId": 99999}
        result = await schema.execute(mutation, variable_values=variables)

        assert result.errors is None
        assert result.data["trackArtist"]["success"] is False
        assert "not found" in result.data["trackArtist"]["message"].lower()

    async def test_untrack_artist_mutation(self):
        """Test artist untracking mutation."""
        # Create test data
        tracked_artist = await sync_to_async(Artist.objects.create)(
            name="Tracked Artist", gid="tracked123", tracked=True
        )

        mutation = """
        mutation UntrackArtist($artistId: Int!) {
            untrackArtist(artistId: $artistId) {
                success
                message
                artist {
                    id
                    name
                    isTracked
                }
            }
        }
        """

        variables = {"artistId": tracked_artist.id}
        result = await schema.execute(mutation, variable_values=variables)

        assert result.errors is None
        assert result.data["untrackArtist"]["success"] is True
        # GraphQL model uses isTracked field name
        assert result.data["untrackArtist"]["artist"]["isTracked"] is False
