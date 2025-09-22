"""Integration test configuration and fixtures with proper PostgreSQL isolation."""

import os

from django.test import override_settings

import pytest


def get_test_database_name():
    """Generate unique test database name for parallel execution."""
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")
    if worker_id == "master":
        return "test_spotify_library_manager"
    else:
        return f"test_spotify_library_manager_{worker_id}"


@pytest.fixture(scope="session")
def django_db_setup_override():
    """Override database settings for better test isolation with PostgreSQL."""
    with override_settings(
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": get_test_database_name(),
                "USER": "slm_user",
                "PASSWORD": "slm_dev_password",
                "HOST": "postgres",
                "PORT": "5432",
                "OPTIONS": {
                    "connect_timeout": 10,
                },
                "TEST": {
                    "NAME": get_test_database_name(),
                    "CREATE_DB": True,
                    "USER": "slm_user",
                    "PASSWORD": "slm_dev_password",
                    "HOST": "postgres",
                    "PORT": "5432",
                    "OPTIONS": {
                        "autocommit": True,
                    },
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
