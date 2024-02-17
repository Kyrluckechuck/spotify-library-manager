import django.core.validators
from django.db import models
from django_stubs_ext.db.models import TypedModelMeta

# Create your models here.
class Artist(models.Model):
    name = models.CharField(max_length=200)
    gid = models.CharField(max_length=120, unique=True)
    tracked = models.BooleanField(default=False)

    @property
    def number_songs(self):
        return ContributingArtist.objects.filter(artist=self).count

    @property
    def albums(self):
        album_base = Album.objects.filter(artist=self)
        return {
            'known': album_base.count,
            'missing': album_base.filter(wanted=True, downloaded=False).count,
            'downloaded': album_base.filter(downloaded=True).count,
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

    @property
    def contributing_artists(self):
        return ContributingArtist.objects.filter(song=self).exclude(artist=self.primary_artist)

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

class Album(models.Model):
    spotify_gid = models.CharField(max_length=2048, unique=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, to_field="gid", db_column="artist_gid")
    spotify_uri = models.CharField(max_length=2048)
    downloaded = models.BooleanField(default=False)
    total_tracks = models.IntegerField(default=0)
    wanted = models.BooleanField(default=True)
    name = models.CharField(max_length=2048)

    class Meta(TypedModelMeta):
        pass

class TrackedPlaylist(models.Model):
    name = models.CharField(max_length=2048)
    url = models.CharField(max_length=2048, unique=True)
    enabled = models.BooleanField(default=True)
    last_synced = models.DateTimeField(default=None, null=True)

    class Meta(TypedModelMeta):
        pass
