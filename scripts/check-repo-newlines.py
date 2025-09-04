#!/usr/bin/env python3

"""
Repo-wide newline checker and fixer
This script checks and fixes trailing newlines across the entire repository.
"""

import sys
import subprocess
from typing import List
from pathlib import Path

# File extensions to check
EXTENSIONS = {
    '.js', '.ts', '.tsx', '.jsx', '.json', '.md', '.txt', 
    '.graphql', '.gql', '.yml', '.yaml', '.toml', '.ini',
    '.css', '.scss', '.sass', '.html', '.xml', '.svg',
    '.py', '.pyx', '.pxd', '.pxi', '.pyi', '.pyw',
    '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.hh',
    '.sh', '.bash', '.zsh', '.fish', '.ps1',
    '.sql', '.sqlite', '.db',
    '.conf', '.cfg', '.config',
    '.lock', '.log'
}

# Files without extensions that should be checked
EXTENSIONLESS_FILES = {
    'Makefile', 'makefile', 'GNUmakefile',
    'Dockerfile', 'Containerfile',
    'pre-commit', 'post-commit', 'pre-push', 'post-receive',
    'prepare-commit-msg', 'commit-msg', 'post-update', 'pre-receive'
}

# Directories to ignore
IGNORE_DIRS = {
    'node_modules', 'dist', 'build', 'coverage', '.git',
    '.husky', '.vscode', '.idea', '__pycache__', '.pytest_cache',
    '.mypy_cache', '.venv', 'venv', 'env', '.env',
    'htmlcov', '.coverage', 'target', 'bin', 'obj'
}

def should_check_file(file_path: Path) -> bool:
    """Check if a file should be checked for trailing newlines."""
    # Check if it's in an ignored directory first
    for part in file_path.parts:
        if part in IGNORE_DIRS:
            return False
    
    # Check if it's a file with a relevant extension
    if file_path.suffix in EXTENSIONS:
        return True
    
    # Check if it's a known extensionless file
    if file_path.name in EXTENSIONLESS_FILES:
        return True
    
    return False

def check_file_newline(file_path: Path) -> bool:
    """Check if a file ends with a newline."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content.endswith('\n') or len(content) == 0
    except (UnicodeDecodeError, PermissionError, OSError):
        # Skip binary files or files we can't read
        return True

def fix_file_newline(file_path: Path) -> bool:
    """Add newline to a file if it doesn't have one."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.endswith('\n') and len(content) > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content + '\n')
            return True
        return False
    except (UnicodeDecodeError, PermissionError, OSError):
        return False

def find_files_to_check(root_path: Path) -> list[Path]:
    """Find all files that should be checked for trailing newlines."""
    files_to_check = []
    
    for file_path in root_path.rglob('*'):
        if file_path.is_file() and should_check_file(file_path):
            files_to_check.append(file_path)
    
    return files_to_check


def get_staged_files(repo_root: Path) -> List[Path]:
    """Return staged files as Paths relative to repo_root, filtered by should_check_file."""
    try:
        # Get list of staged file paths (added, copied, modified, renamed)
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
        )
        staged_paths = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        staged_paths = []

    files: List[Path] = []
    for rel_path in staged_paths:
        candidate = repo_root / rel_path
        if candidate.is_file() and should_check_file(candidate):
            files.append(candidate)
    return files

def main():
    """Main function to check or fix newlines."""
    if len(sys.argv) < 2:
        print("Usage: python check-repo-newlines.py [check|fix] [--staged]")
        sys.exit(1)

    action = sys.argv[1]
    if action not in ["check", "fix"]:
        print("Usage: python check-repo-newlines.py [check|fix] [--staged]")
        sys.exit(1)

    # Get the repository root (assuming script is in scripts/ directory)
    repo_root = Path(__file__).parent.parent

    # Scope selection: default to entire repo unless --staged is provided
    use_staged_only = "--staged" in sys.argv[2:]
    if use_staged_only:
        files_to_check = get_staged_files(repo_root)
    else:
        files_to_check = find_files_to_check(repo_root)
    
    if action == 'check':
        print("🔍 Checking for files without trailing newlines...")
        files_without_newlines = []
        
        for file_path in files_to_check:
            if not check_file_newline(file_path):
                files_without_newlines.append(file_path)
        
        if not files_without_newlines:
            print("✅ All files end with newlines!")
            return
        
        print(f"\n❌ Found {len(files_without_newlines)} files without trailing newlines:")
        for file_path in files_without_newlines:
            relative_path = file_path.relative_to(repo_root)
            print(f"  • {relative_path}")
        
        print("\n💡 To fix these files, run:")
        if use_staged_only:
            print("  python scripts/check-repo-newlines.py fix --staged")
        else:
            print("  python scripts/check-repo-newlines.py fix")
        sys.exit(1)

    elif action == 'fix':
        print("🔧 Fixing files without trailing newlines...")
        fixed_files = []
        
        for file_path in files_to_check:
            if not check_file_newline(file_path):
                if fix_file_newline(file_path):
                    fixed_files.append(file_path)
        
        if not fixed_files:
            print("✅ All files already end with newlines!")
            return
        
        print(f"\n✅ Fixed {len(fixed_files)} files:")
        for file_path in fixed_files:
            relative_path = file_path.relative_to(repo_root)
            print(f"  • {relative_path}")

if __name__ == '__main__':
    main() 
