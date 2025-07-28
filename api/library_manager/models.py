import django.core.validators
from django.db import models
from django.db.models import Sum
from django_stubs_ext.db.models import TypedModelMeta
from django.utils import timezone

# TODO: Make this configurable, allowing "appears_on" to optionally be requested, or others be de-selected
ALBUM_TYPES_TO_DOWNLOAD = ["single", "album", "compilation"]
EXTRA_GROUPS_TO_IGNORE = ["appears_on"]

# Create your models here.
class Artist(models.Model):
    name = models.CharField(max_length=200)
    gid = models.CharField(max_length=120, unique=True)
    tracked = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)
    last_synced_at = models.DateTimeField(default=None, null=True)

    @property
    def number_songs(self):
        return ContributingArtist.objects.filter(artist=self).count()

    @property
    def albums(self):
        album_base = Album.objects.filter(artist=self, album_type__in=ALBUM_TYPES_TO_DOWNLOAD).exclude(album_group__in=EXTRA_GROUPS_TO_IGNORE)
        return {
            'known': album_base.count(),
            'missing': album_base.filter(wanted=True, downloaded=False).count(),
            'downloaded': album_base.filter(downloaded=True).count(),
            'songs': {
                'missing': album_base.filter(wanted=True, downloaded=False).aggregate(Sum('total_tracks'))['total_tracks__sum'] or 0,
            },
        }

    class Meta(TypedModelMeta):
        indexes = [
            models.Index(fields=['gid',]),
            models.Index(fields=['tracked',]),
        ]

    def __str__(self):
        return f"name: {self.name} | gid: {self.gid} | tracked: {self.tracked}"

class Song(models.Model):
    name = models.CharField(max_length=200)
    gid = models.CharField(max_length=120, unique=True)
    primary_artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    failed_count = models.IntegerField(default=0)
    bitrate = models.IntegerField(default=0)
    unavailable = models.BooleanField(default=False)
    file_path = models.FilePathField(null=True)
    downloaded = models.BooleanField(default=False)

    @property
    def contributing_artists(self):
        return ContributingArtist.objects.filter(song=self).exclude(artist=self.primary_artist)
    
    @property
    def spotify_uri(self):
        return f"spotify:track:{self.gid}"
    
    def increment_failed_count(self):
        self.failed_count += 1
        if self.failed_count > 3:
            self.unavailable = True
        self.save()

    class Meta(TypedModelMeta):
        indexes = [
            models.Index(fields=['gid',]),
        ]

    def __str__(self):
        return f"name: {self.name} | gid: {self.gid} | primary_artist: '{self.primary_artist}'"

class ContributingArtist(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)

    class Meta(TypedModelMeta):
        unique_together = ('song', 'artist',)

    def __str__(self):
        return f"S: {self.song.name} | A: {self.artist.name}"

class DownloadHistory(models.Model):
    url = models.CharField(max_length=2048)
    added_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(default=None, null=True)
    progress = models.SmallIntegerField(
        default=0,
        validators=[
            django.core.validators.MinValueValidator(1),
            django.core.validators.MaxValueValidator(1000),
        ],
    )

    @property
    def progress_percent(self) -> float:
        return self.progress / 10

    class Meta(TypedModelMeta):
        pass


class TaskHistory(models.Model):
    TASK_TYPES = [
        ('SYNC', 'Sync'),
        ('DOWNLOAD', 'Download'),
        ('FETCH', 'Fetch'),
    ]
    
    ENTITY_TYPES = [
        ('ARTIST', 'Artist'),
        ('ALBUM', 'Album'),
        ('PLAYLIST', 'Playlist'),
        ('TRACK', 'Track'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    task_id = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=20, choices=TASK_TYPES)
    entity_id = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    progress_percentage = models.FloatField(default=0.0)
    log_messages = models.JSONField(default=list, blank=True)
    last_heartbeat = models.DateTimeField(auto_now_add=True)
    timeout_minutes = models.IntegerField(default=30)  # Default 30 minute timeout
    
    class Meta(TypedModelMeta):
        ordering = ['-started_at']
        
    def __str__(self):
        return f"{self.type} - {self.entity_type} {self.entity_id} ({self.status})"
        
    def add_log_message(self, message: str):
        """Add a log message to the task history"""
        if not self.log_messages:
            self.log_messages = []
        self.log_messages.append({
            'timestamp': timezone.now().isoformat(),
            'message': message
        })
        self.save(update_fields=['log_messages'])
        
    def mark_completed(self, duration_seconds: int = None):
        """Mark the task as completed"""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        if duration_seconds is None:
            duration_seconds = int((self.completed_at - self.started_at).total_seconds())
        self.duration_seconds = duration_seconds
        self.progress_percentage = 100.0
        self.save()
        
    def mark_failed(self, error_message: str = None):
        """Mark the task as failed"""
        self.status = 'FAILED'
        self.completed_at = timezone.now()
        if error_message:
            self.error_message = error_message
        self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())
        self.save()
        
    def update_progress(self, percentage: float):
        """Update the progress percentage"""
        self.progress_percentage = min(100.0, max(0.0, percentage))
        self.save(update_fields=['progress_percentage'])

    def update_heartbeat(self):
        """Update the last heartbeat timestamp"""
        self.save(update_fields=['last_heartbeat'])

    def get_expected_duration_minutes(self) -> int:
        """Get expected duration based on task type and entity"""
        if self.type == 'SYNC':
            return 5  # Sync operations should be quick
        elif self.type == 'DOWNLOAD':
            if self.entity_type == 'PLAYLIST':
                return 15  # Playlist downloads can take longer
            elif self.entity_type == 'ALBUM':
                return 10  # Album downloads
        elif self.type == 'FETCH':
            return 3  # Fetch operations should be fast
        return 30  # Default fallback

    def is_stuck(self) -> bool:
        """Check if the task is stuck using multiple detection methods"""
        from django.utils import timezone
        from datetime import timedelta
        
        if self.status != 'RUNNING':
            return False
        
        # Method 1: Check Huey task state
        try:
            from huey_monitor.models import TaskModel
            huey_task = TaskModel.objects.filter(task_id=self.task_id).first()
            if huey_task:
                # If Huey says it's finished but we're still running, we're stuck
                if huey_task.finished and self.status == 'RUNNING':
                    return True
                # If Huey task doesn't exist but we're running, we're stuck
                if not huey_task and self.status == 'RUNNING':
                    return True
        except Exception:
            pass
        
        # Method 2: Task-specific timeout
        expected_duration = self.get_expected_duration_minutes()
        timeout_threshold = timezone.now() - timedelta(minutes=expected_duration)
        if self.last_heartbeat < timeout_threshold:
            return True
        
        # Method 3: Progress-based detection
        if self.log_messages:
            last_log = max(self.log_messages, key=lambda x: x.get('timestamp', ''))
            if last_log.get('timestamp'):
                try:
                    last_log_dt = timezone.datetime.fromisoformat(
                        last_log['timestamp'].replace('Z', '+00:00')
                    )
                    # If no progress for 5 minutes, likely stuck
                    if timezone.now() - last_log_dt > timedelta(minutes=5):
                        return True
                except Exception:
                    pass
        
        return False

    def mark_stuck(self, reason: str = "Task timeout"):
        """Mark the task as stuck/failed due to timeout"""
        from django.utils import timezone
        
        self.status = 'FAILED'
        self.completed_at = timezone.now()
        self.error_message = f"{reason} - Last heartbeat: {self.last_heartbeat}"
        self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())
        self.save()

    @classmethod
    def cleanup_stuck_tasks(cls):
        """Find and mark stuck tasks as failed"""
        stuck_tasks = cls.objects.filter(status='RUNNING')
        stuck_count = 0
        
        for task in stuck_tasks:
            if task.is_stuck():
                task.mark_stuck("Task timeout - automatic cleanup")
                stuck_count += 1
        
        return stuck_count

class Album(models.Model):
    spotify_gid = models.CharField(max_length=2048, unique=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, to_field="gid", db_column="artist_gid")
    spotify_uri = models.CharField(max_length=2048)
    downloaded = models.BooleanField(default=False)
    total_tracks = models.IntegerField(default=0)
    wanted = models.BooleanField(default=True)
    name = models.CharField(max_length=2048)
    failed_count = models.IntegerField(default=0)
    album_type = models.CharField(max_length=100, null=True)
    album_group = models.CharField(max_length=100, null=True)

    @property
    def desired_album_type(self):
        return self.album_type in ALBUM_TYPES_TO_DOWNLOAD and self.album_group not in EXTRA_GROUPS_TO_IGNORE

    class Meta(TypedModelMeta):
        pass

class TrackedPlaylist(models.Model):
    name = models.CharField(max_length=2048)
    url = models.CharField(max_length=2048, unique=True)
    enabled = models.BooleanField(default=True)
    auto_track_artists = models.BooleanField(default=False)
    last_synced_at = models.DateTimeField(default=None, null=True)

    class Meta(TypedModelMeta):
        pass
