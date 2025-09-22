from pathlib import Path
from typing import Optional

import django.core.validators
from django.conf import settings
from django.db import models
from django.db.models import QuerySet, Sum
from django.utils import timezone

from django_stubs_ext.db.models import TypedModelMeta

# Album selection configuration
#
# These are read from Django settings (Dynaconf-backed), which in turn load from
# `/config/settings.yaml` automatically in containers. Operators should configure
# values there. Environment variables can still override via Dynaconf if needed.
#
# Accepted formats in settings:
# - List, e.g. ["single", "album", "compilation"]
# - Comma-separated string, e.g. "single,album,compilation"


def _get_setting_list(name: str, default: list[str]) -> list[str]:
    value = getattr(settings, name, default)
    if isinstance(value, str):
        parsed = [item.strip() for item in value.split(",") if item.strip()]
        return parsed or default
    if isinstance(value, (list, tuple)):
        # Normalize to list[str]
        return [str(item) for item in value if str(item).strip()]
    return default


ALBUM_TYPES_TO_DOWNLOAD = _get_setting_list(
    "ALBUM_TYPES_TO_DOWNLOAD", ["single", "album", "compilation"]
)
ALBUM_GROUPS_TO_IGNORE = _get_setting_list("ALBUM_GROUPS_TO_IGNORE", ["appears_on"])


# Create your models here.
class FilePath(models.Model):
    """Deduplicated file paths to save storage space."""

    id: models.BigAutoField = models.BigAutoField(primary_key=True)
    path: models.TextField = models.TextField(unique=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    class Meta(TypedModelMeta):
        app_label = "library_manager"
        db_table = "file_paths"
        indexes = [
            models.Index(fields=["path"]),
        ]

    def __str__(self) -> str:
        return str(self.path)


class Artist(models.Model):
    id: models.BigAutoField = models.BigAutoField(primary_key=True)
    name: models.CharField = models.CharField(max_length=500)
    gid: models.CharField = models.CharField(max_length=120, unique=True)
    tracked: models.BooleanField = models.BooleanField(default=False)
    added_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    last_synced_at: models.DateTimeField = models.DateTimeField(default=None, null=True)

    @property
    def number_songs(self) -> int:
        return ContributingArtist.objects.filter(artist=self).count()

    @property
    def spotify_uri(self) -> str:
        return f"spotify:artist:{self.gid}"

    @property
    def albums(self) -> dict:
        album_base = Album.objects.filter(
            artist=self, album_type__in=ALBUM_TYPES_TO_DOWNLOAD
        ).exclude(album_group__in=ALBUM_GROUPS_TO_IGNORE)
        return {
            "known": album_base.count(),
            "missing": album_base.filter(wanted=True, downloaded=False).count(),
            "downloaded": album_base.filter(downloaded=True).count(),
            "songs": {
                "missing": album_base.filter(wanted=True, downloaded=False).aggregate(
                    Sum("total_tracks")
                )["total_tracks__sum"]
                or 0,
            },
        }

    class Meta(TypedModelMeta):
        app_label = "library_manager"
        db_table = "artists"
        indexes = [
            models.Index(
                fields=[
                    "gid",
                ]
            ),
            models.Index(
                fields=[
                    "tracked",
                ]
            ),
        ]

    def __str__(self) -> str:
        return f"name: {self.name} | gid: {self.gid} | tracked: {self.tracked}"


class Song(models.Model):
    id: models.BigAutoField = models.BigAutoField(primary_key=True)
    name: models.CharField = models.CharField(max_length=500)
    gid: models.CharField = models.CharField(max_length=120, unique=True)
    primary_artist: models.ForeignKey = models.ForeignKey(
        Artist, on_delete=models.CASCADE
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    failed_count: models.IntegerField = models.IntegerField(default=0)
    bitrate: models.IntegerField = models.IntegerField(default=0)
    unavailable: models.BooleanField = models.BooleanField(default=False)
    file_path_ref: models.ForeignKey = models.ForeignKey(
        FilePath, on_delete=models.SET_NULL, null=True, blank=True, related_name="songs"
    )
    downloaded: models.BooleanField = models.BooleanField(default=False)

    @property
    def file_path(self) -> str | None:
        """Get the file path string for backward compatibility."""
        return self.file_path_ref.path if self.file_path_ref else None

    @property
    def path(self) -> Path | None:
        """Get the file path as a Path object for filesystem operations."""
        return Path(self.file_path_ref.path) if self.file_path_ref else None

    @file_path.setter
    def file_path(self, path: str | None) -> None:
        """Set the file path using the existing method."""
        self.set_file_path(path)

    def set_file_path(self, path: str | None) -> None:
        """Set the file path, creating/reusing FilePath object."""
        if path is None:
            self.file_path_ref = None
        else:
            file_path_obj, created = FilePath.objects.get_or_create(path=path)
            self.file_path_ref = file_path_obj

    @property
    def contributing_artists(self) -> "QuerySet[ContributingArtist]":
        return ContributingArtist.objects.filter(song=self).exclude(
            artist=self.primary_artist
        )

    @property
    def spotify_uri(self) -> str:
        return f"spotify:track:{self.gid}"

    def increment_failed_count(self) -> None:
        self.failed_count += 1
        if self.failed_count > 3:
            self.unavailable = True
        self.save()

    class Meta(TypedModelMeta):
        app_label = "library_manager"
        db_table = "songs"
        indexes = [
            models.Index(
                fields=[
                    "gid",
                ]
            ),
        ]

    def __str__(self) -> str:
        return f"name: {self.name} | gid: {self.gid} | primary_artist: '{self.primary_artist}'"


class ContributingArtist(models.Model):
    song: models.ForeignKey = models.ForeignKey(Song, on_delete=models.CASCADE)
    artist: models.ForeignKey = models.ForeignKey(Artist, on_delete=models.CASCADE)

    class Meta(TypedModelMeta):
        app_label = "library_manager"
        db_table = "contributing_artists"
        unique_together = (
            "song",
            "artist",
        )

    def __str__(self) -> str:
        return f"S: {self.song.name} | A: {self.artist.name}"


class DownloadHistory(models.Model):
    url: models.CharField = models.CharField(max_length=2048)
    added_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    completed_at: models.DateTimeField = models.DateTimeField(default=None, null=True)
    progress: models.SmallIntegerField = models.SmallIntegerField(
        default=0,
        validators=[
            django.core.validators.MinValueValidator(1),
            django.core.validators.MaxValueValidator(1000),
        ],
    )

    @property
    def progress_percent(self) -> float:
        return float(self.progress) / 10.0

    class Meta(TypedModelMeta):
        app_label = "library_manager"
        db_table = "download_history"


class TaskHistory(models.Model):
    TASK_TYPES = [
        ("SYNC", "Sync"),
        ("DOWNLOAD", "Download"),
        ("FETCH", "Fetch"),
    ]

    ENTITY_TYPES = [
        ("ARTIST", "Artist"),
        ("ALBUM", "Album"),
        ("PLAYLIST", "Playlist"),
        ("TRACK", "Track"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("RUNNING", "Running"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    task_id: models.CharField = models.CharField(max_length=255, unique=True)
    type: models.CharField = models.CharField(max_length=20, choices=TASK_TYPES)
    entity_id: models.CharField = models.CharField(max_length=255)
    entity_type: models.CharField = models.CharField(
        max_length=20, choices=ENTITY_TYPES
    )
    status: models.CharField = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="PENDING"
    )
    started_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    completed_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    error_message: models.TextField = models.TextField(null=True, blank=True)
    duration_seconds: models.IntegerField = models.IntegerField(null=True, blank=True)
    progress_percentage: models.FloatField = models.FloatField(default=0.0)
    log_messages: models.JSONField = models.JSONField(default=list, blank=True)
    last_heartbeat: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    timeout_minutes: models.IntegerField = models.IntegerField(
        default=30
    )  # Default 30 minute timeout

    class Meta(TypedModelMeta):
        app_label = "library_manager"
        db_table = "task_history"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["status", "-started_at"]),
            models.Index(fields=["type", "-started_at"]),
            models.Index(fields=["entity_type", "-started_at"]),
            models.Index(fields=["completed_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.type} - {self.entity_type} {self.entity_id} ({self.status})"

    def add_log_message(self, message: str, max_logs: int = 50) -> None:
        """Add a log message to the task history with automatic truncation"""
        if not self.log_messages:
            self.log_messages = []

        # Add new log message
        self.log_messages.append(
            {"timestamp": timezone.now().isoformat(), "message": message}
        )

        # Truncate if we exceed max_logs
        if len(self.log_messages) > max_logs:
            self.log_messages = self.log_messages[-max_logs:]

        self.save(update_fields=["log_messages"])

    def mark_completed(self, duration_seconds: Optional[int] = None) -> None:
        """Mark the task as completed"""
        self.status = "COMPLETED"
        self.completed_at = timezone.now()
        if duration_seconds is None:
            duration_seconds = int(
                (self.completed_at - self.started_at).total_seconds()
            )
        self.duration_seconds = duration_seconds
        self.progress_percentage = 100.0
        self.save()

    def mark_failed(self, error_message: Optional[str] = None) -> None:
        """Mark the task as failed"""
        self.status = "FAILED"
        self.completed_at = timezone.now()
        if error_message:
            self.error_message = error_message
        self.duration_seconds = int(
            (self.completed_at - self.started_at).total_seconds()
        )
        self.save()

    def update_progress(self, percentage: float) -> None:
        """Update the progress percentage"""
        self.progress_percentage = min(100.0, max(0.0, percentage))
        self.save(update_fields=["progress_percentage"])

    def update_heartbeat(self) -> None:
        """Update the last heartbeat timestamp (no log message added)"""
        self.save(update_fields=["last_heartbeat"])

    def get_expected_duration_minutes(self) -> int:
        """Get expected duration based on task type and entity"""
        if self.type == "SYNC":
            return 5  # Sync operations should be quick
        if self.type == "DOWNLOAD":
            if self.entity_type == "PLAYLIST":
                return 15  # Playlist downloads can take longer
            if self.entity_type == "ALBUM":
                return 10  # Album downloads
        if self.type == "FETCH":
            return 3  # Fetch operations should be fast
        return 30  # Default fallback

    def is_stuck(self) -> bool:
        """Check if the task is stuck using multiple detection methods"""
        from datetime import timedelta

        from django.utils import timezone

        if self.status != "RUNNING":
            return False

        # Method 1: Check Celery task state
        try:
            # TODO: Implement Celery-based task state checking
            # from django_celery_results.models import TaskResult
            # celery_task = TaskResult.objects.filter(task_id=self.task_id).first()
            # if celery_task and celery_task.status in ['SUCCESS', 'FAILURE', 'REVOKED']:
            #     if self.status == "RUNNING":
            #         return True
            pass
        except Exception:
            pass

        # Method 2: Task-specific timeout
        expected_duration = self.get_expected_duration_minutes()
        timeout_threshold = timezone.now() - timedelta(minutes=expected_duration)
        if self.last_heartbeat < timeout_threshold:
            return True

        # Method 3: Progress-based detection
        if self.log_messages:
            last_log = max(self.log_messages, key=lambda x: x.get("timestamp", ""))
            if last_log.get("timestamp"):
                try:
                    from datetime import datetime

                    last_log_dt = datetime.fromisoformat(
                        last_log["timestamp"].replace("Z", "+00:00")
                    )
                    # If no progress for 5 minutes, likely stuck
                    if timezone.now() - last_log_dt > timedelta(minutes=5):
                        return True
                except Exception:
                    pass

        return False

    def mark_stuck(self, reason: str = "Task timeout") -> None:
        """Mark the task as stuck/failed due to timeout"""
        from django.utils import timezone

        self.status = "FAILED"
        self.completed_at = timezone.now()
        self.error_message = f"{reason} - Last heartbeat: {self.last_heartbeat}"
        self.duration_seconds = int(
            (self.completed_at - self.started_at).total_seconds()
        )
        self.save()

    @classmethod
    def cleanup_stuck_tasks(cls) -> int:
        """Find and mark stuck tasks as failed"""
        stuck_tasks = cls.objects.filter(status="RUNNING")
        stuck_count = 0

        for task in stuck_tasks:
            if task.is_stuck():
                task.mark_stuck("Task timeout - automatic cleanup")
                stuck_count += 1

        return stuck_count

    @classmethod
    def cleanup_old_tasks(cls, days_to_keep: int = 30) -> int:
        """Remove completed/failed tasks older than specified days"""
        from datetime import timedelta

        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        deleted_count = cls.objects.filter(
            status__in=["COMPLETED", "FAILED"], started_at__lt=cutoff_date
        ).delete()[0]
        return deleted_count

    @classmethod
    def get_storage_stats(cls) -> dict:
        """Get storage statistics for TaskHistory"""
        total_tasks = cls.objects.count()
        completed_tasks = cls.objects.filter(status="COMPLETED").count()
        failed_tasks = cls.objects.filter(status="FAILED").count()
        running_tasks = cls.objects.filter(status="RUNNING").count()
        pending_tasks = cls.objects.filter(status="PENDING").count()

        # Calculate average log messages per task
        tasks_with_logs = cls.objects.filter(log_messages__isnull=False).exclude(
            log_messages=[]
        )
        avg_logs = 0.0
        if tasks_with_logs.exists():
            total_logs = sum(len(task.log_messages) for task in tasks_with_logs)
            avg_logs = total_logs / tasks_with_logs.count()

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "running_tasks": running_tasks,
            "pending_tasks": pending_tasks,
            "average_logs_per_task": round(avg_logs, 2),
            "tasks_with_logs": tasks_with_logs.count(),
        }


class Album(models.Model):
    spotify_gid: models.CharField = models.CharField(max_length=2048, unique=True)
    artist: models.ForeignKey = models.ForeignKey(
        Artist, on_delete=models.CASCADE, to_field="gid", db_column="artist_gid"
    )
    spotify_uri: models.CharField = models.CharField(max_length=2048)
    downloaded: models.BooleanField = models.BooleanField(default=False)
    total_tracks: models.IntegerField = models.IntegerField(default=0)
    wanted: models.BooleanField = models.BooleanField(default=True)
    name: models.CharField = models.CharField(max_length=2048)
    failed_count: models.IntegerField = models.IntegerField(default=0)
    album_type: models.CharField = models.CharField(max_length=100, null=True)
    album_group: models.CharField = models.CharField(max_length=100, null=True)

    @property
    def desired_album_type(self) -> bool:
        return (
            self.album_type in ALBUM_TYPES_TO_DOWNLOAD
            and self.album_group not in ALBUM_GROUPS_TO_IGNORE
        )

    def __str__(self) -> str:
        return (
            f"name: {self.name} | artist: {self.artist} | downloaded: {self.downloaded}"
        )

    class Meta(TypedModelMeta):
        app_label = "library_manager"
        db_table = "albums"


class TrackedPlaylist(models.Model):
    name: models.CharField = models.CharField(max_length=2048)
    url: models.CharField = models.CharField(max_length=2048, unique=True)
    enabled: models.BooleanField = models.BooleanField(default=True)
    auto_track_artists: models.BooleanField = models.BooleanField(default=False)
    last_synced_at: models.DateTimeField = models.DateTimeField(default=None, null=True)

    def __str__(self) -> str:
        return f"name: {self.name} | url: {self.url} | enabled: {self.enabled}"

    class Meta(TypedModelMeta):
        app_label = "library_manager"
        db_table = "playlists"
