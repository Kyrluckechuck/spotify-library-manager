from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.core.exceptions import ValidationError

from .models import Artist, ContributingArtist, Song
from .forms import DownloadPlaylistForm, ToggleTrackedForm
from .helpers import download_all_for_artist

from spotify_aac_downloader.spotify_aac_downloader import Config, main as downloader_main


def index(request):
    artist_list = Artist.objects.order_by("name")
    # Remove default playlist after
    download_playlist_form = DownloadPlaylistForm({'playlist_url': "https://open.spotify.com/playlist/4RPNYUPhavkcevoTk740I1?si=0113e52f22184213"})
    return render(request, "library_manager/index.html", {"artist_list": artist_list, "playlist_form": download_playlist_form})

def artist(request, artist_id: int):
    artist_details = get_object_or_404(Artist, pk=artist_id)
    artist_songs = ContributingArtist.objects.filter(artist=artist_details)
    form = ToggleTrackedForm({'tracked': artist_details.tracked})
    return render(request, "library_manager/artist.html", {"artist_details": artist_details, "artist_songs": artist_songs, 'form': form})

def song(request, song_id: int):
    song_details = get_object_or_404(Song, pk=song_id)
    return render(request, "library_manager/song.html", {"song_details": song_details})

def track_artist(request, artist_id: int):
    form = ToggleTrackedForm(request.POST)
    if form.is_valid():
        print(form.cleaned_data)
        artist_details = get_object_or_404(Artist, pk=artist_id)
        artist_details.tracked = form.cleaned_data['tracked']
        artist_details.save()
        return HttpResponseRedirect(reverse("library_manager:artist", args=(artist_details.id,)))
    raise ValidationError({'tracked': ["Must be a boolean!",]})

def download_playlist(request):
    playlist_download_form = DownloadPlaylistForm(request.POST)
    if playlist_download_form.is_valid():
        print(playlist_download_form.cleaned_data)
        downloader_config = Config()
        downloader_config.urls = [playlist_download_form.cleaned_data['playlist_url']]
        downloader_config.track_artists = True
        downloader_main(downloader_config)
        return HttpResponseRedirect(reverse("library_manager:index",))
    raise ValidationError({'playlist': ["Must be a valid spotify URL!",]})

def download_all_for_tracked_artists(request):
    all_tracked_artists = Artist.objects.filter(tracked=True)
    for artist in all_tracked_artists:
        print(f"Would attempt for artist {artist}")
        download_all_for_artist(artist)
        return HttpResponseRedirect(reverse("library_manager:index"))
    return HttpResponseRedirect(reverse("library_manager:index"))

def download_all_albums_for_artist(request, artist_id: int):
    artist = get_object_or_404(Artist, pk=artist_id)
    download_all_for_artist(artist)
    return HttpResponseRedirect(reverse("library_manager:artist", args=(artist.id,)))
