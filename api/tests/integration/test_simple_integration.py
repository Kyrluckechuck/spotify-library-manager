"""Simple integration tests for GraphQL functionality."""

import pytest

from src.schema import schema


@pytest.mark.django_db
class TestSimpleIntegration:
    """Test basic GraphQL integration functionality."""

    @pytest.mark.asyncio
    async def test_artists_query_basic(self):
        """Test the artists query."""
        query = "{ artists { totalCount edges { id name } } }"
        result = await schema.execute(query)

        assert result.errors is None
        assert result.data is not None
        assert "artists" in result.data

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
                    isTracked
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
    async def test_cancel_all_tasks_mutation(self):
        """Test cancel all tasks mutation."""
        mutation = """
        mutation {
            cancelAllTasks {
                success
                message
            }
        }
        """
        result = await schema.execute(mutation)

        assert result.errors is None
        assert result.data is not None
        assert "cancelAllTasks" in result.data

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
