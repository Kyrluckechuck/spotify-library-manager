"""Test configuration for api/src tests."""

import os

import django

import pytest

# Configure Django settings for testing
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")
django.setup()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Automatically enable database access for all tests."""
