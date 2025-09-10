#!/usr/bin/env python

import subprocess
import sys
from importlib.metadata import distributions


def get_installed_packages() -> dict[str, str]:
    return {dist.metadata["Name"].lower(): dist.version for dist in distributions()}


def main() -> None:
    # Packages to uninstall (add any that might conflict)
    packages_to_uninstall = [
        "django",
        "django-stubs",
        "django-stubs-ext",
        "django-huey-monitor",
        "huey",
        "strawberry-graphql",
        "fastapi",
        "uvicorn",
        "pydantic",
    ]

    installed = get_installed_packages()

    # Uninstall existing packages
    for package in packages_to_uninstall:
        if package in installed:
            print(f"Uninstalling {package}...")
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", package])

    # Install new requirements
    print("\nInstalling new requirements...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])


if __name__ == "__main__":
    main()
