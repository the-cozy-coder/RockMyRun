from flask import current_app
from .spotify_client import SpotifyClient
from ..models.User import User
from dotenv import load_dotenv
import os

# Load the variables from your .env file into the system environment
load_dotenv()

def get_user_playlists(user_id):
    user = User.query.get(user_id)

    if user is None:
        return []
    
    spotify = SpotifyClient(user.access_token)
    return spotify.get_user_playlists()

def get_playlist_songs(pl_id):
    spotify = SpotifyClient(
        os.environ.get("SPOTIFY_CLIENT_ID"),
        os.environ.get("SPOTIFY_CLIENT_SECRET"),
        os.environ.get("SPOTIFY_REDIRECT_URI")
    )
    return spotify.get_playlist_songs(pl_id)

def create_client() -> SpotifyClient:
    spotify = SpotifyClient(
        os.environ.get("SPOTIFY_CLIENT_ID"),
        os.environ.get("SPOTIFY_CLIENT_SECRET"),
        os.environ.get("SPOTIFY_REDIRECT_URI")
    )
    return spotify

def get_spotify_track_id(title, artist, spotify=None):
    if spotify is None:
        spotify=create_client()
    return spotify.search_spotify_track_id(title, artist, limit = 1), spotify
        
