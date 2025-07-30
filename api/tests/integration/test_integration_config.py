"""Integration test configuration with better database settings."""

from django.test import override_settings

import pytest


@pytest.fixture(scope="session")
def django_db_setup_override():
    """Override database settings for integration tests."""
    with override_settings(
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
                "OPTIONS": {
                    "timeout": 60,
                    "check_same_thread": False,
                    "isolation_level": None,  # Autocommit mode
                },
            }
        }
    ):
        yield


@pytest.fixture(scope="function")
def integration_db(django_db_setup_override):
    """Provide database access for integration tests."""
    from django.db import connection

    # Ensure connection is clean
    connection.close()
    connection.connect()

    # Start transaction
    connection.begin()

    yield connection

    # Rollback transaction
    connection.rollback()
    connection.close()


@pytest.fixture(scope="function")
def isolated_integration_db():
    """Provide isolated database access for each test."""
    from django.db import connection

    # Create a new connection for this test
    connection.close()
    connection.connect()

    # Start transaction
    connection.begin()

    yield connection

    # Rollback and close
    connection.rollback()
    connection.close()
