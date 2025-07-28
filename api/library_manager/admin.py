from django.contrib import admin

# Register your models here.

from .models import Artist, ContributingArtist, DownloadHistory, Song, Album, TrackedPlaylist, TaskHistory

admin.site.register(Artist)
admin.site.register(ContributingArtist)
admin.site.register(DownloadHistory)
admin.site.register(Song)
admin.site.register(Album)
admin.site.register(TrackedPlaylist)
admin.site.register(TaskHistory)
