from django.db import models
from django_stubs_ext.db.models import TypedModelMeta

# Create your models here.
class Artist(models.Model):
    name = models.CharField(max_length=200)
    uuid = models.UUIDField(unique=True)
    tracked = models.BooleanField(default=False)

    @property
    def number_songs(self):
        return ContributingArtists.objects.filter(artist=self).count

    class Meta(TypedModelMeta):
        indexes = [
            models.Index(fields=['uuid',]),
            models.Index(fields=['tracked',]),
        ]

    def __str__(self):
        return f"name: {self.name} | uuid: {self.uuid} | tracked: {self.tracked}"

class Song(models.Model):
    name = models.CharField(max_length=200)
    uuid = models.UUIDField(unique=True)
    primary_artist = models.ForeignKey(Artist, on_delete=models.CASCADE)

    @property
    def contributing_artists(self):
        return ContributingArtists.objects.filter(song=self).exclude(artist=self.primary_artist)

    class Meta(TypedModelMeta):
        indexes = [
            models.Index(fields=['uuid',]),
        ]

    def __str__(self):
        return f"name: {self.name} | uuid: {self.uuid} | primary_artist: '{self.primary_artist}'"

class ContributingArtists(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)

    class Meta(TypedModelMeta):
        unique_together = ('song', 'artist',)

    def __str__(self):
        return f"song_name: {self.song.name} | artist_name: {self.artist.name}"
