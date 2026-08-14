from flask import current_app
from .spotify_client import SpotifyClient
from .user_service import get_valid_access_token
from ..models.User import User
from ..models.Playlist import Playlist
from dotenv import load_dotenv
from ..database import db

# Load the variables from your .env file into the system environment
load_dotenv()

def get_user_playlists(user_id):
    user = User.query.get(user_id)

    if user is None:
        return []
    
    access_token = get_valid_access_token(user)
    spotify = SpotifyClient(access_token)
    return spotify.get_user_playlists_from_spotify()

def get_playlist_songs(user_id, pl_id):
    user = User.query.get(user_id)

    if user is None:
        return []
    
    access_token = get_valid_access_token(user)
    spotify = SpotifyClient(access_token)
    return spotify.get_playlist_songs(pl_id)


def get_spotify_track_id(user_id, title, artist, spotify=None):
    current_app.logger.info(
        f"Searching Spotify: title='{title}', artist='{artist}'"
    )
    user = User.query.get(user_id)
    current_app.logger.info(f"user_id={user_id}")
    current_app.logger.info(f"user={user}")
    if spotify is None:
        access_token = get_valid_access_token(user)
        current_app.logger.info(
            f"Token length={len(access_token)}"
        )
        spotify = SpotifyClient(access_token)
    return spotify.search_spotify_track_id(title, artist, limit = 1), spotify


def sync_user_playlists(user_id):
    user = User.query.get(user_id)

    if user is None:
        return []

    access_token = get_valid_access_token(user)
    spotify = SpotifyClient(access_token)

    playlists = spotify.get_user_playlists_from_spotify()

    for playlist in playlists:
        existing = Playlist.query.filter_by(
            spotify_id=playlist["id"],
            user_id=user_id
        ).first()

        if existing is None:
            existing = Playlist(
                spotify_id=playlist["id"],
                name=playlist["name"],
                user_id=user_id
            )
            db.session.add(existing)
        else:
            existing.name = playlist["name"]

    db.session.commit()

    return playlists      

def get_user_playlists_from_db(user_id):
    return Playlist.query.filter_by(
        user_id=user_id
    ).all()

def get_all_playlists(limit=None):

    query = Playlist.query

    if limit:
        query = query.limit(limit)

    return query.all()