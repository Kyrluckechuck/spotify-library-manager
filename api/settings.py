import os
from pathlib import Path

import django_stubs_ext
import dynaconf

django_stubs_ext.monkeypatch()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

# Use dynaconf for configuration management (same as monolith)
settings = dynaconf.DjangoDynaconf(
    __name__,
    PRELOAD_FOR_DYNACONF=[
        "../settings.yaml",
        "*.yaml",
        "/config/settings.yaml",
    ],
    ENVVAR_FOR_DYNACONF="DJANGO_ENV",
    settings_files=[
        "../settings.yaml",
        "*.yaml",
        "/config/settings.yaml",
    ],
    # Override defaults for API-specific settings
    SECRET_KEY=os.getenv("DJANGO_SECRET_KEY", "django-insecure-development-only-key"),
    DEBUG=os.getenv("DJANGO_DEBUG", "True").lower() == "true",
    ALLOWED_HOSTS=["*"],
    # API-specific installed apps (keeping core Django + adding API needs)
    INSTALLED_APPS=[
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django_stubs_ext",
        "bx_django_utils",
        "django_celery_results",
        "django_celery_beat",
        "kombu.transport.sqlalchemy",
        "library_manager",
        # Dev-only apps may be appended below when DEBUG is true
    ],
    # API-specific middleware (simpler than full web app)
    MIDDLEWARE=[
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ],
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ],
    ROOT_URLCONF="urls",
    STATIC_ROOT=BASE_DIR / "staticfiles",
    STATIC_URL="/static/",
    # Database: PostgreSQL for better concurrent access
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "spotify_library_manager"),
            "USER": os.getenv("POSTGRES_USER", "slm_user"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "slm_dev_password"),
            "HOST": os.getenv("POSTGRES_HOST", "localhost"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
            "OPTIONS": {
                "connect_timeout": 10,
            },
        }
    },
    # Celery Configuration - SQLAlchemy + PostgreSQL broker
    CELERY_BROKER_URL=(
        f"sqlalchemy+postgresql://"
        f"{os.getenv('POSTGRES_USER', 'slm_user')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'slm_dev_password')}@"
        f"{os.getenv('POSTGRES_HOST', 'localhost')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'spotify_library_manager')}"
    ),
    CELERY_RESULT_BACKEND="django-db",
    CELERY_ACCEPT_CONTENT=["json"],
    CELERY_TASK_SERIALIZER="json",
    CELERY_RESULT_SERIALIZER="json",
    CELERY_TIMEZONE="UTC",
    CELERY_TASK_TRACK_STARTED=True,
    CELERY_RESULT_EXTENDED=True,
    CELERY_TASK_TIME_LIMIT=30 * 60,  # 30 minutes
    CELERY_BEAT_SCHEDULER="django_celery_beat.schedulers:DatabaseScheduler",
    # Store additional task metadata
    CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS={
        "master_name": "mymaster",
        "visibility_timeout": 3600,
        "retry_policy": {
            "timeout": 5.0,
        },
    },
)


# Internal IPs for development
if settings.DEBUG:  # type: ignore[name-defined]
    INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]  # For Docker, VMs

    try:
        import django_extensions  # noqa: F401

        settings.INSTALLED_APPS.append("django_extensions")
    except Exception:
        pass

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# STATIC_URL is now set in the dynaconf configuration above
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom configuration for spotdl and downloader
# YouTube Music cookies (for high-quality audio downloads via yt-dlp)
youtube_cookies_location = "/config/youtube_music_cookies.txt"

# Spotify OAuth Configuration
spotify_user_auth_enabled = False
# NOTE: Spotify requires 127.0.0.1 instead of localhost
# The system auto-detects the host from requests, but this is the fallback
spotify_redirect_uri = "http://127.0.0.1:5000/auth/spotify/callback"

# Spotify Developer App Credentials (required for OAuth)
# Can be set via environment variables or in /config/settings.yaml
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID", "")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET", "")

# Legacy fallback for backwards compatibility
cookies_location = youtube_cookies_location
po_token = None
log_level = "INFO"
no_lrc = False
overwrite = False
print_exceptions = True

# Logging configuration to reduce verbosity
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "celery": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "library_manager": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
# Storage configuration (replaces deprecated DEFAULT_FILE_STORAGE and STATICFILES_STORAGE)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Note: Using STORAGES configuration above instead of deprecated DEFAULT_FILE_STORAGE and STATICFILES_STORAGE
# The Django deprecation warnings for these settings are unavoidable in Django 5.0 when using dynaconf
