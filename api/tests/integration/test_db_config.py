"""Database configuration for integration tests with proper SQLite isolation."""

from contextlib import asynccontextmanager

from django.db import connection, connections
from django.test import override_settings

import pytest
from asgiref.sync import sync_to_async


@pytest.fixture(scope="session")
def django_db_setup_override():
    """Override database settings for better test isolation."""
    with override_settings(
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
                "OPTIONS": {
                    "timeout": 60,  # Increased timeout
                    "check_same_thread": False,
                    "isolation_level": None,  # Autocommit mode
                },
            }
        }
    ):
        yield


@pytest.fixture(scope="function")
def integration_db(django_db_setup_override, django_db_blocker):
    """Provide isolated database access for integration tests."""
    with django_db_blocker.unblock():
        # Ensure clean state
        connection.close()
        connection.connect()

        # Start transaction
        connection.begin()

        yield

        # Rollback to clean state
        connection.rollback()
        connection.close()


@pytest.fixture(scope="function")
def isolated_integration_db(django_db_setup_override, django_db_blocker):
    """Provide completely isolated database access for each test."""
    with django_db_blocker.unblock():
        # Close all connections
        for conn in connections.all():
            conn.close()

        # Create fresh connection
        connection.connect()

        # Start transaction
        connection.begin()

        yield

        # Clean up
        connection.rollback()
        connection.close()


@pytest.fixture(scope="function")
async def async_integration_db(django_db_setup_override, django_db_blocker):
    """Provide async database access with proper transaction management."""
    with django_db_blocker.unblock():
        # Ensure clean connection
        await sync_to_async(connection.close)()
        await sync_to_async(connection.connect)()

        # Start transaction
        await sync_to_async(connection.begin)()

        yield

        # Clean up
        await sync_to_async(connection.rollback)()
        await sync_to_async(connection.close)()


@asynccontextmanager
async def async_db_transaction():
    """Context manager for async database transactions."""
    # Start transaction
    await sync_to_async(connection.begin)()

    try:
        yield
    finally:
        # Always rollback to ensure clean state
        await sync_to_async(connection.rollback)()


@pytest.fixture(scope="function")
def graphql_test_db(django_db_setup_override, django_db_blocker):
    """Special database fixture for GraphQL tests with proper isolation."""
    with django_db_blocker.unblock():
        # Use in-memory database with proper settings
        connection.close()
        connection.connect()

        # Start transaction
        connection.begin()

        yield

        # Clean up
        connection.rollback()
        connection.close()


@pytest.fixture(scope="function")
def mutation_test_db(django_db_setup_override, django_db_blocker):
    """Database fixture specifically for mutation tests."""
    with django_db_blocker.unblock():
        # Ensure clean state
        connection.close()
        connection.connect()

        # Start transaction
        connection.begin()

        yield

        # Clean up
        connection.rollback()
        connection.close()


# Helper functions for test isolation
def reset_database():
    """Reset the database to a clean state."""
    connection.close()
    connection.connect()
    connection.begin()


async def async_reset_database():
    """Reset the database to a clean state (async version)."""
    await sync_to_async(connection.close)()
    await sync_to_async(connection.connect)()
    await sync_to_async(connection.begin)()


def cleanup_database():
    """Clean up the database after a test."""
    connection.rollback()
    connection.close()


async def async_cleanup_database():
    """Clean up the database after a test (async version)."""
    await sync_to_async(connection.rollback)()
    await sync_to_async(connection.close)()
