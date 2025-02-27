from django.urls import path

from . import views

app_name = "library_manager"
urlpatterns = [
    # ex: /library_manager/
    path("", views.index, name="index"),
    path("download_playlist", views.download_playlist, name="download_playlist"),
    path("download_all_for_tracked_artists", views.download_all_for_tracked_artists, name="download_all_for_tracked_artists"),
    path("fetch_all_for_tracked_artists", views.fetch_all_for_tracked_artists, name="fetch_all_for_tracked_artists"),
    path("download_history", views.download_history, name="download_history"),
    path("failed_songs", views.failed_songs, name="failed_songs"),
    path("tracked_playlists", views.tracked_playlists, name="tracked_playlists"),
    path("tracked_playlists/<int:tracked_playlist_id>/", views.tracked_playlists_prefilled, name="tracked_playlists_prefilled"),
    path("tracked_playlists/<int:tracked_playlist_id>/sync", views.sync_tracked_playlist, name="sync_tracked_playlist"),
    path("tracked_playlists/<int:tracked_playlist_id>/delete", views.delete_tracked_playlist, name="delete_tracked_playlist"),
    path("tracked_playlists/<int:tracked_playlist_id>/sync_artists", views.sync_tracked_playlist_artists, name="sync_tracked_playlist_artists"),
    path("track_playlist", views.track_playlist, name="track_playlist"),
    # path("tracked_playlists/edit", views.edit_tracked_playlists, name="edit_tracked_playlists"),
    # ex: /library_manager/artist/5/
    path("artist/<int:artist_id>/", views.artist, name="artist"),
    path("artist/<int:artist_id>/fetch_all", views.fetch_all_albums_for_artist, name="fetch_all_albums_for_artist"),
    path("artist/<int:artist_id>/download_missing", views.download_wanted_albums_for_artist, name="download_wanted_albums_for_artist"),
    # ex: /library_manager/song/5/
    path("song/<int:song_id>/", views.song, name="song"),
    path("artist/<int:artist_id>/albums", views.albums, name="albums"),
    path("artist/<int:artist_id>/album/<int:album_id>/wanted", views.album_set_wanted, name="album_set_wanted"),
    path("artist/<int:artist_id>/track", views.track_artist, name="track_artist"),
]
