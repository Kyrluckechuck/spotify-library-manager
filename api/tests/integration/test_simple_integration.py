"""Simple integration tests for GraphQL functionality."""

import pytest

from api.src.schema import schema


@pytest.mark.django_db
class TestSimpleIntegration:
    """Test basic GraphQL integration functionality."""

    @pytest.mark.asyncio
    async def test_hello_query(self):
        """Test the hello query."""
        query = "{ hello }"
        result = await schema.execute(query)

        assert result.errors is None
        assert result.data is not None
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
        assert result.data is not None
        assert result.data["artists"]["totalCount"] == 0
        assert result.data["artists"]["edges"] == []

    @pytest.mark.asyncio
    async def test_albums_query_empty(self):
        """Test albums query with no data."""
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
        assert result.data["albums"]["totalCount"] == 0
        assert result.data["albums"]["edges"] == []

    @pytest.mark.asyncio
    async def test_playlists_query_empty(self):
        """Test playlists query with no data."""
        query = """
        {
            playlists(first: 10) {
                totalCount
                edges {
                    id
                    name
                    enabled
                }
            }
        }
        """
        result = await schema.execute(query)

        assert result.errors is None
        assert result.data is not None
        assert result.data["playlists"]["totalCount"] == 0
        assert result.data["playlists"]["edges"] == []

    @pytest.mark.asyncio
    async def test_cleanup_stuck_tasks_mutation(self):
        """Test cleanup stuck tasks mutation."""
        mutation = """
        mutation {
            cleanupStuckTasks {
                success
                message
                cleanedCount
            }
        }
        """
        result = await schema.execute(mutation)

        assert result.errors is None
        assert result.data is not None
        assert result.data["cleanupStuckTasks"]["success"] is True
        assert "cleaned" in result.data["cleanupStuckTasks"]["message"].lower()

    @pytest.mark.asyncio
    async def test_invalid_query(self):
        """Test handling of invalid query."""
        query = """
        query {
            nonexistentField
        }
        """
        result = await schema.execute(query)

        assert result.errors is not None
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_invalid_mutation(self):
        """Test handling of invalid mutation."""
        mutation = """
        mutation {
            nonexistentMutation {
                success
            }
        }
        """
        result = await schema.execute(mutation)

        assert result.errors is not None
        assert len(result.errors) > 0
