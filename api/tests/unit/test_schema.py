"""Unit tests for GraphQL schema."""

import pytest

from api.src.schema import schema


@pytest.mark.django_db
class TestSchemaQueries:
    """Test GraphQL query resolvers."""

    @pytest.mark.asyncio
    async def test_artists_query(self):
        """Test artists query."""
        query = """
        query {
            artists {
                totalCount
                edges {
                    id
                    name
                }
            }
        }
        """

        result = await schema.execute(query)

        assert result.errors is None
        assert result.data is not None
        assert "artists" in result.data


@pytest.mark.django_db
class TestSchemaMutations:
    """Test GraphQL mutation resolvers."""

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


@pytest.mark.django_db
class TestSchemaErrorHandling:
    """Test GraphQL schema error handling."""

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
