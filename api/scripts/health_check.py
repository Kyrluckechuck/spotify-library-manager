#!/usr/bin/env python3
"""
Health check script with detailed debugging information.
This script provides better error reporting for Docker health checks in CI environments.
"""

import json
import sys
import urllib.request
from datetime import datetime
from urllib.error import HTTPError, URLError


def main() -> None:
    """Run health check with detailed error reporting."""
    try:
        print("🔍 Starting health check...")
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        print("🌐 Attempting to connect to http://localhost:5000/healthz")

        response = urllib.request.urlopen("http://localhost:5000/healthz")
        data = response.read().decode()
        print(f"📡 Health check response: {data}")
        print(f"📊 Response status code: {response.getcode()}")
        print(f"📋 Response headers: {dict(response.headers)}")

        result = json.loads(data)
        status = result.get("status")
        db = result.get("db")

        print(f"✅ Parsed - Status: {status}, DB: {db}")

        if status == "ok" and db:
            print("🎉 Health check passed successfully")
            sys.exit(0)
        else:
            print(f"❌ Health check failed - status: {status}, db: {db}")
            sys.exit(1)

    except HTTPError as e:
        print(f"❌ HTTP Error: {e.code} - {e.reason}")
        sys.exit(1)
    except URLError as e:
        print(f"❌ URL Error: {e.reason}")
        print("Server may not be running or accessible")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ JSON Decode Error: {e}")
        print(f"Response was: {data}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
