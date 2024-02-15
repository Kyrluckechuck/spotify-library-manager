from django import forms
from django.core.validators import URLValidator

class ToggleTrackedForm(forms.Form):
    tracked = forms.BooleanField(required=False)

class DownloadPlaylistForm(forms.Form):
    playlist_url = forms.URLField(
        label='Enter a URL',
        validators=[URLValidator()],
        widget=forms.TextInput(attrs={'placeholder': 'https://open.spotify.com/album/6eUW0wxWtzkFdaEFsTJto6?si=tDyOWtIVSuKAxeTEEVdkhw'})
    )
    tracked = forms.BooleanField(required=False, initial=False)
