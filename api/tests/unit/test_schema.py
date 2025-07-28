"""Unit tests for GraphQL schema."""
import pytest
from unittest.mock import patch
from api.src.schema import schema


@pytest.mark.django_db
class TestSchemaQueries:
    """Test GraphQL query resolvers."""
    
    @pytest.mark.asyncio
    async def test_hello_query(self):
        """Test hello query."""
        query = """
        query {
            hello
        }
        """
        
        result = await schema.execute(query)
        
        assert result.errors is None
        assert result.data is not None
        assert result.data['hello'] == "Hello from Spotify Library Manager API!"


@pytest.mark.django_db
class TestSchemaMutations:
    """Test GraphQL mutation resolvers."""
    
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
        
        with patch('api.src.schema.DjangoTaskHistory.cleanup_stuck_tasks') as mock_cleanup:
            mock_cleanup.return_value = 5
            
            result = await schema.execute(mutation)
            
            assert result.errors is None
            assert result.data is not None
            assert result.data['cleanupStuckTasks']['success'] is True
            assert result.data['cleanupStuckTasks']['cleanedCount'] == 5


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