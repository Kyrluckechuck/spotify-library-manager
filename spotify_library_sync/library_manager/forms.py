from django import forms
from library_manager.validators import SpotifyValidator

class ToggleTrackedForm(forms.Form):
    tracked = forms.BooleanField(required=False)

class DownloadPlaylistForm(forms.Form):
    playlist_url = forms.Field(
        label='Enter a URL',
        validators=[SpotifyValidator()],
        widget=forms.TextInput(attrs={'placeholder': 'https://open.spotify.com/album/6eUW0wxWtzkFdaEFsTJto6?si=tDyOWtIVSuKAxeTEEVdkhw'})
    )
    tracked = forms.BooleanField(required=False, initial=False)
    force_playlist_resync = forms.BooleanField(required=False, initial=False)

class TrackedPlaylistForm(forms.Form):
    playlist_url = forms.Field(
        label='Enter a URL',
        validators=[SpotifyValidator()],
        widget=forms.TextInput(attrs={'placeholder': 'https://open.spotify.com/album/6eUW0wxWtzkFdaEFsTJto6?si=tDyOWtIVSuKAxeTEEVdkhw'})
    )
    name = forms.CharField(
        label='Playlist Name',
        strip=True,
        empty_value='Playlist Name',
        min_length=3,
        widget=forms.TextInput(attrs={'placeholder': 'Playlist name'}),
    )
    enabled = forms.BooleanField(required=False, initial=True)
    auto_track_artists = forms.BooleanField(required=False, initial=False)
