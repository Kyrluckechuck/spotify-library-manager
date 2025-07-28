"""Integration tests for GraphQL mutations."""
import pytest
from django.test import TransactionTestCase
from asgiref.sync import sync_to_async
from api.src.schema import schema


@pytest.mark.graphql
class TestArtistMutations(TransactionTestCase):
    """Test GraphQL mutations for artists."""
    
    @pytest.mark.asyncio
    async def test_track_artist_mutation_success(self, mutation_test_db, untracked_artist):
        """Test successful artist tracking mutation."""
        mutation = f"""
        mutation {{
            trackArtist(artistId: {untracked_artist.id}) {{
                success
                message
                artist {{
                    id
                    name
                    tracked
                }}
            }}
        }}
        """
        result = await schema.execute(mutation)
        
        assert result.errors is None
        assert result.data["trackArtist"]["success"] is True
        assert result.data["trackArtist"]["artist"]["tracked"] is True
        
        # Verify in database using async operation
        await sync_to_async(untracked_artist.refresh_from_db)()
        assert untracked_artist.tracked is True
    
    @pytest.mark.asyncio
    async def test_untrack_artist_mutation_success(self, mutation_test_db, sample_artist):
        """Test successful artist untracking mutation."""
        mutation = f"""
        mutation {{
            untrackArtist(artistId: {sample_artist.id}) {{
                success
                message
                artist {{
                    id
                    name
                    tracked
                }}
            }}
        }}
        """
        result = await schema.execute(mutation)
        
        assert result.errors is None
        assert result.data["untrackArtist"]["success"] is True
        assert result.data["untrackArtist"]["artist"]["tracked"] is False
        
        # Verify in database using async operation
        await sync_to_async(sample_artist.refresh_from_db)()
        assert sample_artist.tracked is False
    
    @pytest.mark.asyncio
    async def test_track_nonexistent_artist(self, mutation_test_db):
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


@pytest.mark.graphql
class TestAlbumMutations(TransactionTestCase):
    """Test GraphQL mutations for albums."""
    
    @pytest.mark.asyncio
    async def test_mark_album_wanted(self, mutation_test_db, sample_album):
        """Test marking album as wanted."""
        mutation = f"""
        mutation {{
            setAlbumWanted(albumId: {sample_album.id}, wanted: true) {{
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
        assert result.data["setAlbumWanted"]["success"] is True
        assert result.data["setAlbumWanted"]["album"]["wanted"] is True
        
        # Verify in database using async operation
        await sync_to_async(sample_album.refresh_from_db)()
        assert sample_album.wanted is True
    
    @pytest.mark.asyncio
    async def test_mark_album_unwanted(self, mutation_test_db, sample_album):
        """Test marking album as unwanted."""
        # First mark as wanted using async operation
        await sync_to_async(setattr)(sample_album, 'wanted', True)
        await sync_to_async(sample_album.save)()
        
        mutation = f"""
        mutation {{
            setAlbumWanted(albumId: {sample_album.id}, wanted: false) {{
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
        assert result.data["setAlbumWanted"]["success"] is True
        assert result.data["setAlbumWanted"]["album"]["wanted"] is False
        
        # Verify in database using async operation
        await sync_to_async(sample_album.refresh_from_db)()
        assert sample_album.wanted is False


@pytest.mark.graphql
class TestPlaylistMutations(TransactionTestCase):
    """Test GraphQL mutations for playlists."""
    
    @pytest.mark.asyncio
    async def test_enable_playlist(self, mutation_test_db, sample_playlist):
        """Test enabling a playlist."""
        # First disable the playlist using async operation
        await sync_to_async(setattr)(sample_playlist, 'enabled', False)
        await sync_to_async(sample_playlist.save)()
        
        mutation = f"""
        mutation {{
            togglePlaylist(playlistId: {sample_playlist.id}) {{
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
        assert result.data["togglePlaylist"]["success"] is True
        assert result.data["togglePlaylist"]["playlist"]["enabled"] is True
        
        # Verify in database using async operation
        await sync_to_async(sample_playlist.refresh_from_db)()
        assert sample_playlist.enabled is True
    
    @pytest.mark.asyncio
    async def test_disable_playlist(self, mutation_test_db, sample_playlist):
        """Test disabling a playlist."""
        mutation = f"""
        mutation {{
            togglePlaylist(playlistId: {sample_playlist.id}) {{
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
        assert result.data["togglePlaylist"]["success"] is True
        assert result.data["togglePlaylist"]["playlist"]["enabled"] is False
        
        # Verify in database using async operation
        await sync_to_async(sample_playlist.refresh_from_db)()
        assert sample_playlist.enabled is False


@pytest.mark.graphql
class TestTaskMutations(TransactionTestCase):
    """Test GraphQL mutations for tasks."""
    
    @pytest.mark.asyncio
    async def test_cleanup_stuck_tasks(self, mutation_test_db):
        """Test cleaning up stuck tasks."""
        mutation = """
        mutation {
            cleanupStuckTasks {
                success
                message
                count
            }
        }
        """
        result = await schema.execute(mutation)
        
        assert result.errors is None
        assert result.data["cleanupStuckTasks"]["success"] is True
        assert "cleanup" in result.data["cleanupStuckTasks"]["message"].lower() 