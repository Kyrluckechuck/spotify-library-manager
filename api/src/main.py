"""Main FastAPI application module. Sets up Django before any ORM/model usage."""

# pylint: disable=wrong-import-position

import logging
import os
import sys
from pathlib import Path

import django
from django.conf import settings as dj_settings
from django.db import connections

from asgiref.sync import sync_to_async
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from starlette.staticfiles import StaticFiles
from strawberry.fastapi import GraphQLRouter

# Add the API directory to Python path for Django apps
API_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(API_DIR))

# Set up Django before importing any models or using ORM
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

# Import the complete schema after Django setup. During static analysis this import
# may fail before Django is configured; we import within create_app to avoid E402.


class Settings:
    """Application settings."""

    _instance: "Settings | None" = None
    _initialized: bool

    def __new__(cls) -> "Settings":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._initialized = True

        self.title = "Spotify Library Manager API"
        self.version = "1.0.0"
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        self.host = os.getenv("HOST", "127.0.0.1")

        # Handle invalid port values gracefully
        try:
            self.port = int(os.getenv("PORT", "8000"))
        except ValueError:
            self.port = 8000  # Default fallback

        self.reload = os.getenv("RELOAD", "False").lower() == "true"

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton for testing purposes."""
        cls._instance = None


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(title=settings.title, version=settings.version, debug=settings.debug)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Local import to ensure Django setup is complete and satisfy flake8 E402
    from .schema import schema  # pylint: disable=import-error,no-name-in-module

    graphql_app = GraphQLRouter(schema)
    app.include_router(graphql_app, prefix="/graphql")

    # Serve Django static files
    static_root = getattr(dj_settings, "STATIC_ROOT", None)
    if static_root:
        app.mount("/static", StaticFiles(directory=str(static_root)), name="static")

    # Serve built frontend
    frontend_dir = API_DIR / "frontend-dist"
    if frontend_dir.exists():
        app.mount(
            "/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend"
        )

    # Run configuration validation after app is fully constructed
    # (function defined below)
    _validate_runtime_configuration()

    @app.get("/healthz")
    async def healthcheck() -> dict[str, object]:
        """Basic health endpoint with DB check."""

        @sync_to_async
        def check_db() -> bool:
            try:
                with connections["default"].cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                return True
            except Exception as e:
                logging.getLogger("api.healthcheck").error(
                    "Database health check failed: %s", e
                )
                return False

        db_ok = await check_db()
        return {"status": "ok", "db": db_ok}

    @app.get("/{full_path:path}", response_model=None)
    async def spa_fallback(
        full_path: str,
    ) -> PlainTextResponse | FileResponse:
        # Let GraphQL routes be handled by their router; return 404 on GET if it falls through
        if full_path.startswith("graphql"):
            return PlainTextResponse("Not Found", status_code=404)
        # Serve index.html for SPA routes only when frontend assets are present
        if frontend_dir.exists():
            return FileResponse(frontend_dir / "index.html")
        # In local dev (make dev), frontend runs on Vite dev server; do not error here
        return PlainTextResponse("Not Found", status_code=404)

    return app


def _validate_runtime_configuration() -> None:
    """Validate important runtime settings and log actionable warnings.

    Does not raise; only logs warnings so local tests/dev aren't blocked.
    """
    logger = logging.getLogger("api.config")

    # Cookies file for downloader
    cookies_path_str = getattr(dj_settings, "cookies_location", "/config/cookies.txt")
    cookies_path = Path(str(cookies_path_str))
    try:
        if not cookies_path.exists():
            logger.warning(
                "cookies_location not found at %s. Place your Spotify cookies.txt there or set 'cookies_location' in /config/settings.yaml",
                cookies_path,
            )
    except PermissionError:
        logger.warning(
            "Cannot access cookies_location at %s due to permission error. Service will continue without cookies.",
            cookies_path,
        )

    # Album selection lists
    album_types = getattr(
        dj_settings, "ALBUM_TYPES_TO_DOWNLOAD", ["single", "album", "compilation"]
    )
    if not isinstance(album_types, (list, tuple)) or not album_types:
        logger.warning(
            "ALBUM_TYPES_TO_DOWNLOAD is not configured as a non-empty list. Check /config/settings.yaml"
        )

    album_groups_ignore = getattr(dj_settings, "ALBUM_GROUPS_TO_IGNORE", ["appears_on"])
    if not isinstance(album_groups_ignore, (list, tuple)):
        logger.warning(
            "ALBUM_GROUPS_TO_IGNORE should be a list. Check /config/settings.yaml"
        )

    # Final path exists check (optional)
    final_path = getattr(dj_settings, "final_path", None)
    if final_path:
        try:
            final_path_obj = Path(str(final_path))
            if not final_path_obj.exists():
                logger.warning(
                    "Configured final_path does not exist: %s. Ensure the host path is mounted into the container.",
                    final_path_obj,
                )
        except Exception:
            # Ignore invalid types
            pass


# Create the default app instance
app = create_app()
