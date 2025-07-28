#!/usr/bin/env python
"""
Test script to verify migration functionality
"""

import subprocess
import sys
from pathlib import Path

def test_migrations():
    """Test the migration functionality"""
    print("Testing migration functionality...")
    
    # Test if we can run the migration check
    api_dir = Path("api")
    env = {"PYTHONPATH": str(api_dir.absolute())}
    
    # Test showmigrations
    result = subprocess.run(
        ["python", "manage.py", "showmigrations", "--list"],
        cwd=api_dir,
        env=env,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Migration check works")
        print("Migration status:")
        print(result.stdout)
    else:
        print("❌ Migration check failed")
        print("Error:", result.stderr)
        return False
    
    # Test database check
    result = subprocess.run(
        ["python", "manage.py", "check", "--database", "default"],
        cwd=api_dir,
        env=env,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Database check works")
    else:
        print("❌ Database check failed")
        print("Error:", result.stderr)
        return False
    
    return True

if __name__ == "__main__":
    if test_migrations():
        print("✅ All migration tests passed")
        sys.exit(0)
    else:
        print("❌ Migration tests failed")
        sys.exit(1) 