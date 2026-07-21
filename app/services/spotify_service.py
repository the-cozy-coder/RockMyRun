from flask import current_app
from .spotify_client import SpotifyClient



def get_user_playlists():

    spotify = SpotifyClient(
        current_app.config["SPOTIFY_CLIENT_ID"],
        current_app.config["SPOTIFY_CLIENT_SECRET"],
        current_app.config["SPOTIFY_REDIRECT_URI"]
    )

    return spotify.get_user_playlists()

def get_playlist_songs(pl_id):
    spotify = SpotifyClient(
        current_app.config["SPOTIFY_CLIENT_ID"],
        current_app.config["SPOTIFY_CLIENT_SECRET"],
        current_app.config["SPOTIFY_REDIRECT_URI"]
    )

    songs = []

    results = spotify.playlist_tracks(pl_id)
    return results
        
