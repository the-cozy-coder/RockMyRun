from flask import current_app
from .spotify_client import SpotifyClient
from dotenv import load_dotenv
import os

# Load the variables from your .env file into the system environment
load_dotenv()

def get_user_playlists():
    spotify = SpotifyClient(
        os.environ.get("SPOTIFY_CLIENT_ID"),
        os.environ.get("SPOTIFY_CLIENT_SECRET"),
        os.environ.get("SPOTIFY_REDIRECT_URI")
    )

    return spotify.get_user_playlists()

def get_playlist_songs(pl_id):
    spotify = SpotifyClient(
        os.environ.get("SPOTIFY_CLIENT_ID"),
        os.environ.get("SPOTIFY_CLIENT_SECRET"),
        os.environ.get("SPOTIFY_REDIRECT_URI")
    )
    print("+++++++++++++++++++++++++++++++++++")
    print(
        os.environ.get("SPOTIFY_CLIENT_ID"),
        os.environ.get("SPOTIFY_CLIENT_SECRET"),
        os.environ.get("SPOTIFY_REDIRECT_URI")
    )
    results = spotify.get_playlist_songs(pl_id)
    return results
        
