from django.db import models
from django_stubs_ext.db.models import TypedModelMeta

# Create your models here.
class Artist(models.Model):
    name = models.CharField(max_length=200)
    uuid = models.UUIDField()
    tracked = models.BooleanField(default=False)

    @property
    def number_songs(self):
        return self.song_set.count

    class Meta(TypedModelMeta):
        indexes = [
            models.Index(fields=['uuid',]),
            models.Index(fields=['tracked',]),
        ]

    def __str__(self):
        return f"name: {self.name} | uuid: {self.uuid} | tracked: {self.tracked}"

class Song(models.Model):
    name = models.CharField(max_length=200)
    uuid = models.UUIDField()
    primary_artist = models.ForeignKey(Artist, on_delete=models.CASCADE)

    class Meta(TypedModelMeta):
        indexes = [
            models.Index(fields=['uuid',]),
        ]

    def __str__(self):
        return f"name: {self.name} | uuid: {self.uuid} | primary_artist: {self.primary_artist}"
