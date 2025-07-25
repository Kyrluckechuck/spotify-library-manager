"""Main FastAPI application module. Sets up Django before any ORM/model usage."""
import os
import sys
from pathlib import Path
import django
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

# Add the API directory to Python path for Django apps
API_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(API_DIR))

# Set up Django before importing any models or using ORM
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

# Import the complete schema
from .schema import schema

app = FastAPI(title="Spotify Library Manager API", version="1.0.0")
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql") 