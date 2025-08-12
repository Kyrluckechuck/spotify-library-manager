"""Main FastAPI application module. Sets up Django before any ORM/model usage."""
# pylint: disable=wrong-import-position

import os
import sys
from pathlib import Path

import django

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from fastapi.responses import FileResponse, PlainTextResponse
from starlette.staticfiles import StaticFiles
from django.db import connections
from django.conf import settings as dj_settings

# Add the API directory to Python path for Django apps
API_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(API_DIR))

# Set up Django before importing any models or using ORM
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

# Import the complete schema after Django setup. During static analysis this import
# may fail before Django is configured; suppress the false-positive for linting.
from .schema import schema  # noqa: E402  # pylint: disable=import-error,no-name-in-module


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

    graphql_app = GraphQLRouter(schema)
    app.include_router(graphql_app, prefix="/graphql")

    # Serve Django static files
    static_root = getattr(dj_settings, "STATIC_ROOT", None)
    if static_root:
        app.mount("/static", StaticFiles(directory=str(static_root)), name="static")

    # Serve built frontend
    frontend_dir = API_DIR / "frontend-dist"
    if frontend_dir.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

    @app.get("/healthz")
    async def healthcheck() -> dict[str, object]:
        """Basic health endpoint with DB check."""
        db_ok = True
        try:
            with connections["default"].cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception:  # noqa: BLE001 - surface as boolean only
            db_ok = False
        return {"status": "ok", "db": db_ok}

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):  # noqa: ANN201, ARG001 - FastAPI infers response, path captured for SPA
        # Let GraphQL routes be handled by their router; return 404 on GET if it falls through
        if full_path.startswith("graphql"):
            return PlainTextResponse("Not Found", status_code=404)
        # Serve index.html for SPA routes only when frontend assets are present
        if frontend_dir.exists():
            return FileResponse(frontend_dir / "index.html")
        # In local dev (make dev), frontend runs on Vite dev server; do not error here
        return PlainTextResponse("Not Found", status_code=404)

    return app


# Create the default app instance
app = create_app()
