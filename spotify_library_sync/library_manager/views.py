from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models.functions import Lower
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import Artist, ContributingArtist, DownloadHistory, Song
from .forms import DownloadPlaylistForm, ToggleTrackedForm
from . import helpers

def index(request: HttpRequest):
    search_term = request.GET.get("search_artist")
    tracked_term = request.GET.get("tracked")
    raw_artist_list = Artist.objects
    search_term_and_page = '?'
    if search_term is not None:
        raw_artist_list = raw_artist_list.filter(name__icontains=search_term)
        search_term_and_page += f"search_artist={search_term}&"
    if tracked_term is not None:
        tracked_artists = tracked_term is True or tracked_term.lower() == 'true'
        raw_artist_list = raw_artist_list.filter(tracked=tracked_artists)
        search_term_and_page += f"tracked={tracked_artists}&"
    search_term_and_page += 'page'
    artist_list = raw_artist_list.order_by(Lower("name")).all()
    paginator = Paginator(artist_list, 50)
    # Remove default playlist after
    download_playlist_form = DownloadPlaylistForm()
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "library_manager/index.html", {"playlist_form": download_playlist_form, "page_obj": page_obj, "search_term_and_page": search_term_and_page})

def artist(request: HttpRequest, artist_id: int):
    artist_details = get_object_or_404(Artist, pk=artist_id)
    artist_songs = ContributingArtist.objects.filter(artist=artist_details)
    form = ToggleTrackedForm({'tracked': artist_details.tracked})
    return render(request, "library_manager/artist.html", {"artist_details": artist_details, "artist_songs": artist_songs, 'form': form})

def song(request: HttpRequest, song_id: int):
    song_details = get_object_or_404(Song, pk=song_id)
    return render(request, "library_manager/song.html", {"song_details": song_details})

def track_artist(request: HttpRequest, artist_id: int):
    form = ToggleTrackedForm(request.POST)
    if form.is_valid():
        artist_details = get_object_or_404(Artist, pk=artist_id)
        artist_details.tracked = form.cleaned_data['tracked']
        artist_details.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    raise ValidationError({'tracked': ["Must be a boolean!",]})

def download_playlist(request: HttpRequest):
    playlist_download_form = DownloadPlaylistForm(request.POST)
    if playlist_download_form.is_valid():
        helpers.download_playlist(playlist_download_form.cleaned_data['playlist_url'], playlist_download_form.cleaned_data['tracked'])
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    print(playlist_download_form)
    print(playlist_download_form.errors)
    raise ValidationError({'playlist': ["Must be a valid spotify URL!",]})

def download_history(request: HttpRequest):
    download_history_not_done = DownloadHistory.objects.filter(completed_at=None).order_by("-added_at")
    download_history_done = DownloadHistory.objects.exclude(completed_at=None).order_by("-added_at")[:50]
    download_playlist_form = DownloadPlaylistForm()
    return render(request, "library_manager/download_history.html", {"download_history_not_done": download_history_not_done, "download_history_done": download_history_done, "playlist_form": download_playlist_form})

def download_all_for_tracked_artists(request: HttpRequest):
    all_tracked_artists = Artist.objects.filter(tracked=True)
    print("Disabled for now, but let's finish this off")
    print("would have downloaded for")
    print(all_tracked_artists)
    # for artist in all_tracked_artists:
    #     helpers.download_all_for_artist(artist.id)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def download_all_albums_for_artist(request: HttpRequest, artist_id: int):
    artist = get_object_or_404(Artist, pk=artist_id)
    helpers.download_all_for_artist(artist.id)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
