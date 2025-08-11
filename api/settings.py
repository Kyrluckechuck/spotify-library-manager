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
        "huey.contrib.djhuey",
        "huey_monitor",
        "library_manager",
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
    # Database: use same location as monolith by default
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "/config/db/db.sqlite3",  # Same as monolith
            "OPTIONS": {
                "timeout": 20,
            },
        }
    },
    # Huey: basic configuration for development
    HUEY={
        "huey_class": "huey.SqliteHuey",
        "name": "spotify_library_manager",
        "filename": Path("/config/db/huey.sqlite3"),
        "immediate": False,
        "results": True,
        "store_none": False,
    },
)

# Ensure /config/db/ directory exists (same as monolith)
Path("/config/db/").mkdir(parents=True, exist_ok=True)

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# STATIC_URL is now set in the dynaconf configuration above
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom configuration for spotdl and downloader
cookies_location = "/config/cookies.txt"
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
        "huey": {
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
