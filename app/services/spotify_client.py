import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import current_app

class SpotifyClient:

    def __init__(self, access_token):
        self.sp_client = spotipy.Spotify(
            auth=access_token
        )


    def search_spotify_track_id(self, title, artist, limit:int = 10):
        """Search for a Spotify track ID given a title and artist."""
        results = self.sp_client.search(q=f'track:{title} artist:{artist}', 
                                        limit=limit,
                                        type='track')
        track_id = [x.get('id') for x in results['tracks']['items']]
        return track_id

    def get_user_playlists_from_spotify(self):
        user_playlists = self.sp_client.current_user_playlists(limit=50, offset=0)
        owned_playlists = [{"id":pl['id'], "name":pl['name']} for pl in user_playlists['items'] if pl['owner']['id'] == self.sp_client.current_user()['id']]
        return owned_playlists

    def get_playlist_songs(self, playlist_id)->list:
        """Get a list of Spotify track IDs from a playlist."""
        results = self.sp_client.playlist_tracks(playlist_id)
        song_ids = [song['item']['id'] for song in results.get('items', [])]
        return song_ids

def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=current_app.config["SPOTIFY_CLIENT_ID"],
        client_secret=current_app.config["SPOTIFY_CLIENT_SECRET"],
        redirect_uri=current_app.config["SPOTIFY_REDIRECT_URI"],
        scope=(
            "user-library-read "
            "playlist-read-private "
            "playlist-read-collaborative "
            "playlist-modify-public "
            "playlist-modify-private"
        ),
        cache_handler=spotipy.cache_handler.MemoryCacheHandler()
)