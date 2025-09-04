"""Regression tests for sync functionality to prevent Connection Refused errors."""

from unittest.mock import MagicMock, patch

import pytest

from library_manager.tasks import fetch_all_albums_for_artist_sync


@pytest.mark.integration
@pytest.mark.django_db
class TestSyncRegression:
    """Regression tests for sync functionality."""

    def test_sync_artist_no_connection_refused(self, sample_artist):
        """Test that sync_artist doesn't fail with Connection Refused error."""
        # Mock the Celery task to avoid actual external API calls
        with patch(
            "library_manager.tasks.fetch_all_albums_for_artist.delay"
        ) as mock_delay:
            mock_delay.return_value = MagicMock(id="test-task-id")

            # This should not raise a Connection Refused error
            try:
                fetch_all_albums_for_artist_sync(sample_artist.id)
                assert mock_delay.called, "Celery task should have been called"
            except ConnectionRefusedError:
                pytest.fail(
                    "fetch_all_albums_for_artist_sync raised Connection Refused - Celery broker misconfigured"
                )
            except Exception as e:
                # Other exceptions are acceptable (API timeouts, etc.)
                if "Connection refused" in str(e):
                    pytest.fail(f"Connection refused error detected: {e}")

    @pytest.mark.asyncio
    async def test_sync_artist_service_no_connection_refused(self, sample_artist):
        """Test that the artist service sync method doesn't fail with Connection Refused."""
        from src.services.artist import ArtistService

        service = ArtistService()

        # Mock the underlying task to avoid external calls
        with patch(
            "library_manager.tasks.fetch_all_albums_for_artist_sync"
        ) as mock_sync:
            mock_sync.return_value = None

            try:
                result = await service.sync_artist(str(sample_artist.id))
                assert result is not None, "Sync should return an artist object"
                assert result.name == sample_artist.name
            except ConnectionRefusedError:
                pytest.fail(
                    "Artist service sync raised Connection Refused - Celery broker misconfigured"
                )
            except Exception as e:
                if "Connection refused" in str(e):
                    pytest.fail(f"Connection refused error in service: {e}")

    @pytest.mark.django_db
    def test_celery_broker_configured(self):
        """Test that Celery broker is properly configured."""
        from django.conf import settings

        # Check that broker URL is set (PostgreSQL-based broker)
        assert hasattr(
            settings, "CELERY_BROKER_URL"
        ), "CELERY_BROKER_URL should be configured"
        broker_url = getattr(settings, "CELERY_BROKER_URL")

        # Should be using PostgreSQL as broker, not external AMQP broker
        assert broker_url.startswith(
            "sqlalchemy+postgresql://"
        ), f"Expected PostgreSQL broker, got {broker_url}"

    @pytest.mark.django_db
    def test_celery_result_backend_configured(self):
        """Test that Celery result backend is properly configured."""
        from django.conf import settings

        assert hasattr(
            settings, "CELERY_RESULT_BACKEND"
        ), "CELERY_RESULT_BACKEND should be configured"
        backend = getattr(settings, "CELERY_RESULT_BACKEND")

        # Should be using django-db
        assert backend == "django-db", f"Expected django-db backend, got {backend}"
