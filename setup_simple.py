#!/usr/bin/env python

import subprocess
import sys
from importlib.metadata import version, PackageNotFoundError
from packaging.specifiers import SpecifierSet
from packaging.version import Version, InvalidVersion

def get_installed_version(package_name):
    try:
        return version(package_name)
    except PackageNotFoundError:
        return None

def version_in_range(version_str, spec):
    try:
        ver = Version(version_str)
        specifier = SpecifierSet(spec)
        return ver in specifier
    except InvalidVersion:
        return False

def check_package_version(package_name, version_spec):
    installed_version = get_installed_version(package_name)
    if not installed_version:
        return False
    return version_in_range(installed_version, version_spec)

def run_pip_command(cmd, ignore_conflicts=False):
    base_cmd = [sys.executable, "-m", "pip"]
    if ignore_conflicts and cmd[0] == "install":
        cmd = ["install", "--no-deps"] + cmd[1:]
    subprocess.run(base_cmd + cmd)

def main():
    # Check pydantic version
    if not check_package_version("pydantic", ">=2.9.2,<3.0.0"):
        print("Installing pydantic from wheels...")
        run_pip_command([
            "install",
            "--only-binary", "pydantic,pydantic-core",
            "pydantic>=2.9.2,<3.0.0"
        ])

    conflicts = {
        "fastapi": ">=0.103.0,<0.104.0",
        "uvicorn": ">=0.23.2,<0.24.0",
        "rich": ">=13.9.4,<14.0.0"
    }

    needs_reinstall = False
    for package, version_spec in conflicts.items():
        if not check_package_version(package, version_spec):
            needs_reinstall = True
            print(f"Package {package} version mismatch. Will reinstall dependencies.")
            break

    if needs_reinstall:
        print("\nUninstalling conflicting packages...")
        run_pip_command([
            "uninstall",
            "-y",
            *conflicts.keys()
        ])

        print("\nInstalling requirements...")
        run_pip_command([
            "install",
            "-r", "requirements.txt"
        ], ignore_conflicts=True)
    else:
        print("\nAll package versions are compatible. No reinstallation needed.")
        run_pip_command([
            "install",
            "-r", "requirements.txt"
        ], ignore_conflicts=True)

if __name__ == "__main__":
    main() 