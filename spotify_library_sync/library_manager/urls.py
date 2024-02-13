from django.urls import path

from . import views

app_name = "library_manager"
urlpatterns = [
    # ex: /library_manager/
    path("", views.index, name="index"),
    path("download_playlist", views.download_playlist, name="download_playlist"),
    path("download_all_for_tracked_artists", views.download_all_for_tracked_artists, name="download_all_for_tracked_artists"),
    # ex: /library_manager/artist/5/
    path("artist/<int:artist_id>/", views.artist, name="artist"),
    # ex: /library_manager/song/5/
    path("song/<int:song_id>/", views.song, name="song"),
    path("artist/<int:artist_id>/track", views.track_artist, name="track_artist"),
]