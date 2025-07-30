from django.contrib import admin

from .models import (
    Album,
    Artist,
    ContributingArtist,
    DownloadHistory,
    Song,
    TaskHistory,
    TrackedPlaylist,
)

# Register your models here.


admin.site.register(Artist)
admin.site.register(ContributingArtist)
admin.site.register(DownloadHistory)
admin.site.register(Song)
admin.site.register(Album)
admin.site.register(TrackedPlaylist)
admin.site.register(TaskHistory)
