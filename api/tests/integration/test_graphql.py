import pytest
from src.schema import schema

@pytest.mark.django_db
@pytest.mark.graphql
class TestArtistQueries:
    """Test GraphQL queries for artists."""
    
    @pytest.mark.asyncio
    async def test_hello_query(self):
        """Test the hello query."""
        query = "{ hello }"
        result = await schema.execute(query)
        assert result.errors is None
        assert result.data["hello"] == "Hello from Spotify Library Manager API!"
    
    @pytest.mark.asyncio
    async def test_artists_query_empty(self):
        """Test artists query with no data."""
        query = """
        {
            artists(first: 10) {
                totalCount
                edges {
                    id
                    name
                    tracked
                }
            }
        }
        """
        result = await schema.execute(query)
        assert result.errors is None
        assert result.data["artists"]["totalCount"] == 0
        assert result.data["artists"]["edges"] == []
    
    @pytest.mark.asyncio
    async def test_artists_query_with_data(self, multiple_artists):
        """Test artists query with sample data."""
        query = """
        {
            artists(first: 10) {
                totalCount
                pageInfo {
                    hasNextPage
                    hasPreviousPage
                }
                edges {
                    id
                    name
                    tracked
                }
            }
        }
        """
        result = await schema.execute(query)
        assert result.errors is None
        assert result.data["artists"]["totalCount"] == 5
        assert len(result.data["artists"]["edges"]) == 5
        assert result.data["artists"]["pageInfo"]["hasNextPage"] is False
    
    @pytest.mark.asyncio
    async def test_artists_query_with_pagination(self, multiple_artists):
        """Test artists query with pagination."""
        query = """
        {
            artists(first: 2) {
                totalCount
                pageInfo {
                    hasNextPage
                    endCursor
                }
                edges {
                    id
                    name
                }
            }
        }
        """
        result = await schema.execute(query)
        assert result.errors is None
        assert result.data["artists"]["totalCount"] == 5
        assert len(result.data["artists"]["edges"]) == 2
        assert result.data["artists"]["pageInfo"]["hasNextPage"] is True
        assert result.data["artists"]["pageInfo"]["endCursor"] is not None
    
    @pytest.mark.asyncio
    async def test_artists_query_with_filter(self, multiple_artists):
        """Test artists query with tracking filter."""
        query = """
        {
            artists(tracked: true, first: 10) {
                totalCount
                edges {
                    id
                    name
                    tracked
                }
            }
        }
        """
        result = await schema.execute(query)
        assert result.errors is None
        # Should only return tracked artists (even indices: 0, 2, 4 = 3 artists)
        assert result.data["artists"]["totalCount"] == 3
        for artist in result.data["artists"]["edges"]:
            assert artist["tracked"] is True
    
    @pytest.mark.asyncio
    async def test_artists_query_with_sorting(self, multiple_artists):
        """Test artists query with sorting."""
        query = """
        {
            artists(sortBy: "name", sortDirection: "asc", first: 10) {
                edges {
                    name
                }
            }
        }
        """
        result = await schema.execute(query)
        assert result.errors is None
        names = [artist["name"] for artist in result.data["artists"]["edges"]]
        # Should be sorted alphabetically
        assert names == sorted(names)

@pytest.mark.django_db
@pytest.mark.graphql
class TestArtistMutations:
    """Test GraphQL mutations for artists."""
    
    @pytest.mark.asyncio
    async def test_track_artist_mutation(self, untracked_artist):
        """Test tracking an artist."""
        mutation = f"""
        mutation {{
            trackArtist(artistId: {untracked_artist.id}) {{
                success
                message
                artist {{
                    id
                    tracked
                }}
            }}
        }}
        """
        result = await schema.execute(mutation)
        assert result.errors is None
        assert result.data["trackArtist"]["success"] is True
        assert result.data["trackArtist"]["artist"]["tracked"] is True
        
        # Verify in database
        untracked_artist.refresh_from_db()
        assert untracked_artist.tracked is True
    
    @pytest.mark.asyncio
    async def test_untrack_artist_mutation(self, sample_artist):
        """Test untracking an artist."""
        mutation = f"""
        mutation {{
            untrackArtist(artistId: {sample_artist.id}) {{
                success
                message
                artist {{
                    id
                    tracked
                }}
            }}
        }}
        """
        result = await schema.execute(mutation)
        assert result.errors is None
        assert result.data["untrackArtist"]["success"] is True
        assert result.data["untrackArtist"]["artist"]["tracked"] is False
        
        # Verify in database
        sample_artist.refresh_from_db()
        assert sample_artist.tracked is False
    
    @pytest.mark.asyncio
    async def test_track_nonexistent_artist(self):
        """Test tracking a non-existent artist."""
        mutation = """
        mutation {
            trackArtist(artistId: 99999) {
                success
                message
            }
        }
        """
        result = await schema.execute(mutation)
        assert result.errors is None
        assert result.data["trackArtist"]["success"] is False
        assert "not found" in result.data["trackArtist"]["message"].lower()

@pytest.mark.django_db
@pytest.mark.graphql
class TestAlbumQueries:
    """Test GraphQL queries for albums."""
    
    @pytest.mark.asyncio
    async def test_albums_query(self, sample_album):
        """Test albums query."""
        query = """
        {
            albums(first: 10) {
                totalCount
                edges {
                    id
                    name
                    wanted
                    downloaded
                }
            }
        }
        """
        result = await schema.execute(query)
        assert result.errors is None
        assert result.data["albums"]["totalCount"] == 1
        assert len(result.data["albums"]["edges"]) == 1
        assert result.data["albums"]["edges"][0]["name"] == "Test Album" 