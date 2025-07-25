#!/usr/bin/env python

import os
import sys
import signal
import subprocess
from pathlib import Path

def run_api():
    api_dir = Path("api")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(api_dir.absolute())
    
    process = subprocess.Popen(
        ["python", "run.py"],
        cwd=api_dir,
        env=env
    )
    return process

def run_frontend():
    frontend_dir = Path("frontend")
    process = subprocess.Popen(
        ["yarn", "dev"],
        cwd=frontend_dir
    )
    return process

def main():
    # Start API server
    print("Starting API server...")
    api_process = run_api()

    # Start frontend dev server
    print("Starting frontend dev server...")
    frontend_process = run_frontend()

    def cleanup(signum, frame):
        print("\nShutting down development servers...")
        api_process.terminate()
        frontend_process.terminate()
        sys.exit(0)

    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    try:
        # Wait for either process to exit
        api_process.wait()
        frontend_process.terminate()
    except KeyboardInterrupt:
        cleanup(None, None)

if __name__ == "__main__":
    main() 