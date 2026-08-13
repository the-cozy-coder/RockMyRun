from flask import current_app
from .spotify_client import SpotifyClient
from .user_service import get_valid_access_token
from ..models.User import User
from dotenv import load_dotenv
import os

# Load the variables from your .env file into the system environment
load_dotenv()

def get_user_playlists(user_id):
    user = User.query.get(user_id)

    if user is None:
        return []
    
    access_token = get_valid_access_token(user)
    spotify = SpotifyClient(access_token)
    return spotify.get_user_playlists()

def get_playlist_songs(user_id, pl_id):
    user = User.query.get(user_id)

    if user is None:
        return []
    
    access_token = get_valid_access_token(user)
    spotify = SpotifyClient(access_token)
    return spotify.get_playlist_songs(pl_id)


def get_spotify_track_id(user_id, title, artist, spotify=None):
    user = User.query.get(user_id)
    current_app.logger.info(f"user_id={user_id}")
    current_app.logger.info(f"user={user}")
    if spotify is None:
        access_token = get_valid_access_token(user)
        spotify = SpotifyClient(access_token)
    return spotify.search_spotify_track_id(title, artist, limit = 1), spotify
        
