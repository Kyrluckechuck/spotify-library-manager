#!/usr/bin/env python
"""
Test script to verify the development setup is working correctly.
This script checks that all three services (API, Frontend, Huey) are running.
"""

import requests
import time
import sys
from pathlib import Path

def check_api_server():
    """Check if the API server is running"""
    try:
        response = requests.get("http://localhost:5000/graphql", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def check_frontend_server():
    """Check if the frontend server is running"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def check_huey_worker():
    """Check if the Huey worker is running by checking the database"""
    try:
        # Check if huey.db exists and has recent activity
        huey_db_path = Path("huey.db")
        if huey_db_path.exists():
            # Check if the file has been modified recently (indicating worker activity)
            import os
            stat = os.stat(huey_db_path)
            # If modified in the last 5 minutes, consider it active
            return (time.time() - stat.st_mtime) < 300
        return False
    except Exception:
        return False

def main():
    print("🔍 Testing development setup...")
    print()
    
    # Wait a bit for services to start
    print("⏳ Waiting for services to start...")
    time.sleep(10)
    
    # Check each service
    services = [
        ("API Server (http://localhost:5000)", check_api_server),
        ("Frontend Server (http://localhost:3000)", check_frontend_server),
        ("Huey Worker", check_huey_worker),
    ]
    
    all_working = True
    
    for service_name, check_func in services:
        print(f"Checking {service_name}...", end=" ")
        if check_func():
            print("✅ Running")
        else:
            print("❌ Not running")
            all_working = False
    
    print()
    
    if all_working:
        print("🎉 All services are running correctly!")
        print()
        print("You can now:")
        print("  • Access the frontend at: http://localhost:3000")
        print("  • Use the GraphQL API at: http://localhost:5000/graphql")
        print("  • Background tasks will be processed by the Huey worker")
        print()
        print("The system is now properly asynchronous!")
    else:
        print("⚠️  Some services are not running correctly.")
        print("Please check the output above and ensure all services started properly.")
        sys.exit(1)

if __name__ == "__main__":
    main() 