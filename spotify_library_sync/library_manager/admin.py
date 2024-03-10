from django.contrib import admin

# Register your models here.

from .models import Artist, ContributingArtist, DownloadHistory, Song

admin.site.register(Artist)
admin.site.register(ContributingArtist)
admin.site.register(DownloadHistory)
admin.site.register(Song)
