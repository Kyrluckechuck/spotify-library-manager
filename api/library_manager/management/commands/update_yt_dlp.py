"""
Django management command to update yt-dlp to the latest version.

Usage:
    python manage.py update_yt_dlp
    docker compose exec web python manage.py update_yt_dlp
    docker compose exec worker python manage.py update_yt_dlp
"""

import subprocess
import sys

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Update yt-dlp to the latest version"

    def add_arguments(self, parser):
        parser.add_argument(
            "--to-master",
            action="store_true",
            help="Update to bleeding edge master branch (yt-dlp --update-to master equivalent)",
        )

    def handle(self, *args, **options):
        self.stdout.write("🔄 Updating yt-dlp...")

        try:
            if options["to_master"]:
                self.stdout.write("📡 Updating to bleeding edge master branch...")
                # Install directly from GitHub master branch
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "--upgrade",
                        "git+https://github.com/yt-dlp/yt-dlp.git@master",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
            else:
                self.stdout.write("📦 Updating to latest stable release...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                    capture_output=True,
                    text=True,
                    check=True,
                )

            self.stdout.write(self.style.SUCCESS("✅ yt-dlp updated successfully!"))

            # Show version info
            version_result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import yt_dlp; print(yt_dlp.version.__version__)",
                ],
                capture_output=True,
                text=True,
            )
            if version_result.returncode == 0:
                self.stdout.write(f"📋 New version: {version_result.stdout.strip()}")

        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to update yt-dlp: {e}"))
            if e.stdout:
                self.stdout.write(f"STDOUT: {e.stdout}")
            if e.stderr:
                self.stdout.write(f"STDERR: {e.stderr}")
            sys.exit(1)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Unexpected error updating yt-dlp: {e}")
            )
            sys.exit(1)
