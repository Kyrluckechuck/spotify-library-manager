#!/usr/bin/env python3
"""
Test script to verify Celery configuration within Docker.
This should be run inside the Docker container.
"""

import os
import sys


def test_celery_config():
    """Test if Celery configuration is working within Docker."""
    try:
        print("🔍 Testing Celery configuration...")

        # Test environment variables
        print(f"✅ CELERY_BROKER_URL: {os.getenv('CELERY_BROKER_URL', 'NOT SET')}")
        print(
            f"✅ CELERY_RESULT_BACKEND: {os.getenv('CELERY_RESULT_BACKEND', 'NOT SET')}"
        )
        print(f"✅ POSTGRES_HOST: {os.getenv('POSTGRES_HOST', 'NOT SET')}")
        print(f"✅ POSTGRES_PORT: {os.getenv('POSTGRES_PORT', 'NOT SET')}")

        # Test Django setup
        print("\n🔍 Setting up Django...")
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

        import django

        django.setup()
        print("✅ Django setup successful")

        # Test Celery imports
        print("\n🔍 Testing Celery imports...")
        from celery import current_app

        print(f"✅ Celery current_app: {current_app}")

        # Test task discovery
        print("\n🔍 Testing task discovery...")
        from library_manager.tasks import fetch_all_albums_for_artist

        print(f"✅ Task imported: {fetch_all_albums_for_artist}")

        # Test Django settings
        print("\n🔍 Testing Django settings...")
        from django.conf import settings

        print(
            f"✅ CELERY_BROKER_URL from settings: {getattr(settings, 'CELERY_BROKER_URL', 'NOT SET')}"
        )
        print(
            f"✅ CELERY_RESULT_BACKEND from settings: {getattr(settings, 'CELERY_RESULT_BACKEND', 'NOT SET')}"
        )

        # Test Redis connection (if Redis is available)
        print("\n🔍 Testing Redis connection...")
        try:
            import redis

            broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
            if broker_url.startswith("redis://"):
                host = broker_url.split("://")[1].split(":")[0]
                port = int(broker_url.split(":")[2].split("/")[0])
                r = redis.Redis(host=host, port=port, socket_connect_timeout=5)
                r.ping()
                print(f"✅ Redis connection successful to {host}:{port}")
            else:
                print("⚠️  Redis broker URL not configured")
        except Exception as e:
            print(f"⚠️  Redis connection test failed: {e}")

        print("\n🎉 Celery configuration test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error testing Celery configuration: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_celery_config()
    sys.exit(0 if success else 1)
