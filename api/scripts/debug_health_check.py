#!/usr/bin/env python3
"""
Advanced health check script specifically for CI debugging.
Provides comprehensive environment and system diagnostics.
"""

import json
import os
import sys
import urllib.request
from datetime import datetime
from urllib.error import HTTPError, URLError


def check_environment():
    """Check and display environment information."""
    print("🌍 === ENVIRONMENT CHECK ===")
    print(f"⏰ Current time: {datetime.now().isoformat()}")
    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"👤 User: {os.getenv('USER', 'unknown')}")
    print(f"🏠 Home: {os.getenv('HOME', 'unknown')}")

    # Check key environment variables
    env_vars = [
        "DJANGO_SECRET_KEY",
        "DJANGO_DEBUG",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_HOST",
        "POSTGRES_PORT",
    ]
    print("\n🔧 Environment variables:")
    for var in env_vars:
        value = os.getenv(var)
        if var in ["DJANGO_SECRET_KEY", "POSTGRES_PASSWORD"]:
            # Mask sensitive values
            masked = (
                f"{value[:5]}...{value[-3:]}" if value and len(value) > 8 else "***"
            )
            print(f"  {var}: {masked}")
        else:
            print(f"  {var}: {value}")


def check_filesystem():
    """Check filesystem and required files."""
    print("\n📂 === FILESYSTEM CHECK ===")

    # Check current directory contents
    try:
        files = os.listdir(".")
        print(f"📋 Files in current directory: {sorted(files)[:10]}...")
    except Exception as e:
        print(f"❌ Error listing directory: {e}")

    # Check for key files
    key_files = ["manage.py", "settings.py", "src/main.py", "scripts/health_check.py"]
    for file_path in key_files:
        exists = os.path.exists(file_path)
        print(f"  {'✅' if exists else '❌'} {file_path}")


def check_database():
    """Check database connectivity."""
    print("\n🗄️ === DATABASE CHECK ===")
    try:
        # Set Django settings if not already configured
        import sys

        sys.path.append("/app")
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

        import django
        from django.conf import settings
        from django.db import connections

        if not settings.configured:
            django.setup()

        print(
            f"⚙️ Django settings module: {os.getenv('DJANGO_SETTINGS_MODULE', 'default')}"
        )
        print(f"🏷️ Database name: {settings.DATABASES['default']['NAME']}")
        print(f"🏠 Database host: {settings.DATABASES['default']['HOST']}")
        print(f"🚪 Database port: {settings.DATABASES['default']['PORT']}")

        # Test database connection
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ Database connected: {version}")

    except Exception as e:
        print(f"❌ Database check failed: {e}")


def check_server_process():
    """Check if server process is running."""
    print("\n🌐 === SERVER PROCESS CHECK ===")
    try:
        import subprocess

        # Try different approaches for process listing
        ps_commands = [
            ["ps", "aux"],
            ["ps", "-ef"],
            ["pgrep", "-fl", "uvicorn"],
            ["pgrep", "-fl", "python"],
        ]

        process_found = False
        for cmd in ps_commands:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    print(f"✅ Process info from {' '.join(cmd)}:")
                    lines = result.stdout.strip().split("\n")
                    for line in lines[:10]:  # Show first 10 lines
                        print(f"  {line}")
                    process_found = True
                    break
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        if not process_found:
            print("❌ No process listing commands available")

        # Check if port 5000 is in use (alternative approach)
        try:
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(("localhost", 5000))
            sock.close()
            if result == 0:
                print("✅ Port 5000 is open (server likely running)")
            else:
                print("❌ Port 5000 is not accessible")
        except Exception as e:
            print(f"❌ Port check failed: {e}")

    except Exception as e:
        print(f"❌ Process check failed: {e}")


def test_health_endpoint():
    """Test the health endpoint with detailed debugging."""
    print("\n🏥 === HEALTH ENDPOINT TEST ===")

    urls_to_try = [
        "http://localhost:5000/healthz",
        "http://127.0.0.1:5000/healthz",
        "http://0.0.0.0:5000/healthz",
    ]

    for url in urls_to_try:
        print(f"\n🌐 Testing: {url}")
        try:
            print(f"⏰ Timestamp: {datetime.now().isoformat()}")
            response = urllib.request.urlopen(url, timeout=10)
            data = response.read().decode()
            print(f"📡 Response: {data}")
            print(f"📊 Status code: {response.getcode()}")
            print(f"📋 Headers: {dict(response.headers)}")

            result = json.loads(data)
            status = result.get("status")
            db = result.get("db")

            print(f"✅ Parsed - Status: {status}, DB: {db}")

            if status == "ok" and db:
                print(f"🎉 Health check passed for {url}")
                return True
            else:
                print(f"⚠️ Health check not fully healthy: status={status}, db={db}")

        except HTTPError as e:
            print(f"❌ HTTP Error: {e.code} - {e.reason}")
        except URLError as e:
            print(f"❌ URL Error: {e.reason}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON Decode Error: {e}")
            print(f"Raw response: {data if 'data' in locals() else 'No data'}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

    return False


def main():
    """Run comprehensive health diagnostics."""
    print("🔍 === COMPREHENSIVE HEALTH DIAGNOSTICS ===")

    check_environment()
    check_filesystem()
    check_database()
    check_server_process()

    if test_health_endpoint():
        print("\n🎉 === DIAGNOSTIC COMPLETE: HEALTHY ===")
        sys.exit(0)
    else:
        print("\n❌ === DIAGNOSTIC COMPLETE: UNHEALTHY ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
