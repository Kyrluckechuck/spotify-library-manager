from django import forms
from django.core.validators import RegexValidator

class ToggleTrackedForm(forms.Form):
    tracked = forms.BooleanField(required=False)

class DownloadPlaylistForm(forms.Form):
    playlist_url = forms.Field(
        label='Enter a URL',
        validators=[RegexValidator(regex=r"^(https:\/\/open.spotify.com\/|spotify:)([a-zA-Z0-9]+)(.*)")],
        widget=forms.TextInput(attrs={'placeholder': 'https://open.spotify.com/album/6eUW0wxWtzkFdaEFsTJto6?si=tDyOWtIVSuKAxeTEEVdkhw'})
    )
    tracked = forms.BooleanField(required=False, initial=False)
