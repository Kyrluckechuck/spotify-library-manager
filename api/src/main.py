"""Main FastAPI application module. Sets up Django before any ORM/model usage."""
import os
import sys
from pathlib import Path
import django
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter


# Add the API directory to Python path for Django apps
API_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(API_DIR))

# Set up Django before importing any models or using ORM
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

# Import the complete schema after Django setup
from .schema import schema  # noqa: E402


class Settings:
    """Application settings."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
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
    def reset(cls):
        """Reset the singleton for testing purposes."""
        cls._instance = None

def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.title,
        version=settings.version,
        debug=settings.debug
    )

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
    
    return app


# Create the default app instance
app = create_app() 