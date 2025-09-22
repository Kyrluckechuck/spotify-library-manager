"""Test-specific Django settings that use PostgreSQL for production parity."""

import os

from settings import *  # noqa: F401,F403


# Support for pytest-xdist parallel execution
# Each worker gets its own test database
def get_test_database_name():
    """Generate unique test database name for parallel execution."""
    worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")
    if worker_id == "master":
        return "test_spotify_library_manager"
    else:
        return f"test_spotify_library_manager_{worker_id}"


# Use PostgreSQL for tests (production parity)
# Connect to the Docker postgres instance but use a separate test database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": get_test_database_name(),
        "USER": os.getenv("POSTGRES_USER", "slm_user"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "slm_dev_password"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "OPTIONS": {
            "connect_timeout": 10,
        },
        "TEST": {
            "NAME": get_test_database_name(),
        },
    }
}

# Use simple password hasher for tests (much faster)
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]


# Disable migrations for tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Disable Celery task execution during tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Disable logging during tests
LOGGING_CONFIG = None
LOGGING = {}

# Use simple cache for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}
