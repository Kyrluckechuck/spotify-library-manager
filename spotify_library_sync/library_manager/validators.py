from django.core.validators import RegexValidator

def SpotifyValidator():
    return RegexValidator(regex=r"^(https:\/\/open.spotify.com\/|spotify:)([a-zA-Z0-9]+)(.*)")
