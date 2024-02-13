from django.contrib import admin

# Register your models here.

from .models import Artist, Song

admin.site.register(Artist)
admin.site.register(Song)
