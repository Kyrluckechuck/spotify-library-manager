"""Docker-specific test settings - uses postgres service name instead of localhost."""

from settings import *  # noqa: F401,F403

# Use PostgreSQL for tests (production parity) inside Docker network
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "test_spotify_library_manager",
        "USER": "slm_user",
        "PASSWORD": "slm_dev_password",
        "HOST": "postgres",  # Docker service name, not localhost
        "PORT": "5432",
        "OPTIONS": {
            "connect_timeout": 10,
        },
        "TEST": {
            "NAME": "test_spotify_library_manager",
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

# Celery configuration for tests - use django-db broker
CELERY_BROKER_URL = "django-db"
CELERY_RESULT_BACKEND = "django-db"

# Disable Celery task execution during tests (run synchronously)
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
