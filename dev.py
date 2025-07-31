#!/usr/bin/env python

import os
import sys
import signal
import subprocess
import threading
import time
from pathlib import Path

def print_with_prefix(prefix, line):
    """Print output with a colored prefix"""
    if line.strip():
        print(f"\033[1;34m[{prefix}]\033[0m {line.strip()}")

def stream_output(process, prefix):
    """Stream process output with prefix"""
    try:
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                print_with_prefix(prefix, line.rstrip())
    except (OSError, ValueError):
        pass

def run_api():
    env = os.environ.copy()
    env["PYTHONPATH"] = "api"
    
    process = subprocess.Popen(
        ["python", "api/run.py"],
        cwd=Path("."),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    return process

def run_frontend():
    process = subprocess.Popen(
        ["yarn", "dev"],
        cwd=Path("frontend"),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    return process

def run_huey_worker():
    """Run the Huey worker for background task processing"""
    env = os.environ.copy()
    env["PYTHONPATH"] = "api"
    env["DJANGO_SETTINGS_MODULE"] = "settings"
    
    process = subprocess.Popen(
        ["python", "api/manage.py", "run_huey"],
        cwd=Path("."),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    return process

def run_migrations():
    """Run Django migrations"""
    env = os.environ.copy()
    env["PYTHONPATH"] = "api"
    env["DJANGO_SETTINGS_MODULE"] = "settings"
    
    print_with_prefix("MIGRATIONS", "Running migrations...")
    
    # Run migrations (Django handles database creation automatically)
    migrate_process = subprocess.run(
        ["python", "api/manage.py", "migrate"],
        cwd=Path("."),
        env=env,
        capture_output=True,
        text=True
    )
    
    if migrate_process.returncode != 0:
        print_with_prefix("ERROR", "Failed to run migrations")
        print_with_prefix("ERROR", migrate_process.stderr)
        return False
    
    print_with_prefix("MIGRATIONS", "Migrations completed successfully")
    return True

def main():
    print("\033[1;32m🚀 Starting Spotify Library Manager Development Servers...\033[0m\n")
    
    # Run migrations first
    print_with_prefix("SETUP", "Checking and running database migrations...")
    if not run_migrations():
        print_with_prefix("ERROR", "Migration check failed. Exiting.")
        sys.exit(1)
    
    # Start API server
    print_with_prefix("SETUP", "Starting API server...")
    api_process = run_api()
    
    # Start frontend dev server  
    print_with_prefix("SETUP", "Starting frontend dev server...")
    frontend_process = run_frontend()
    
    # Start Huey worker for background tasks
    print_with_prefix("SETUP", "Starting Huey worker for background tasks...")
    huey_process = run_huey_worker()
    
    # Wait a moment for servers to start
    time.sleep(3)
    
    # Start output streaming threads
    api_thread = threading.Thread(target=stream_output, args=(api_process, "API"), daemon=True)
    frontend_thread = threading.Thread(target=stream_output, args=(frontend_process, "FRONTEND"), daemon=True)
    huey_thread = threading.Thread(target=stream_output, args=(huey_process, "HUEY"), daemon=True)
    
    api_thread.start()
    frontend_thread.start()
    huey_thread.start()
    
    print_with_prefix("SETUP", "Development servers starting up...")
    print_with_prefix("INFO", "API will be available at: http://localhost:5000/graphql")
    print_with_prefix("INFO", "Frontend will be available at: http://localhost:3000")
    print_with_prefix("INFO", "Huey worker is processing background tasks")
    print_with_prefix("INFO", "Press Ctrl+C to stop all servers\n")

    def cleanup(signum=None, frame=None):
        print_with_prefix("SHUTDOWN", "Shutting down development servers...")
        try:
            api_process.terminate()
            frontend_process.terminate()
            huey_process.terminate()
            # Give processes time to shutdown gracefully
            api_process.wait(timeout=5)
            frontend_process.wait(timeout=5)
            huey_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            api_process.kill()
            frontend_process.kill()
            huey_process.kill()
        except (OSError, ValueError):
            pass
        print_with_prefix("SHUTDOWN", "All servers stopped.")
        sys.exit(0)

    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    try:
        # Keep the main thread alive and monitor processes
        while True:
            # Check if any process has exited
            if api_process.poll() is not None:
                print_with_prefix("ERROR", "API server exited unexpectedly")
                break
            if frontend_process.poll() is not None:
                print_with_prefix("ERROR", "Frontend server exited unexpectedly")
                break
            if huey_process.poll() is not None:
                print_with_prefix("ERROR", "Huey worker exited unexpectedly")
                break
            
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()

if __name__ == "__main__":
    main() 
