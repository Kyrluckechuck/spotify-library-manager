"""Integration test configuration and fixtures with proper SQLite isolation."""

from django.test import override_settings

import pytest


@pytest.fixture(scope="session")
def django_db_setup_override():
    """Override database settings for better test isolation."""
    with override_settings(
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
                "OPTIONS": {
                    "timeout": 120,  # Increased timeout
                    "check_same_thread": False,
                    "isolation_level": None,  # Autocommit mode
                },
            }
        }
    ):
        yield


@pytest.fixture(scope="function")
def graphql_test_db(django_db_setup_override, django_db_blocker):
    """Database fixture for GraphQL tests with proper isolation."""
    with django_db_blocker.unblock():
        yield


@pytest.fixture(scope="function")
def mutation_test_db(django_db_setup_override, django_db_blocker):
    """Database fixture for mutation tests with proper isolation."""
    with django_db_blocker.unblock():
        yield


@pytest.fixture(scope="function")
def integration_db(django_db_setup_override, django_db_blocker):
    """Database fixture for general integration tests."""
    with django_db_blocker.unblock():
        yield


@pytest.fixture(scope="function")
async def async_integration_db(django_db_setup_override, django_db_blocker):
    """Async database fixture for integration tests."""
    with django_db_blocker.unblock():
        yield
