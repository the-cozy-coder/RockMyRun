import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint

class SpotifyClient:
    def __init__(self, client_id, client_secret, callback):
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback = callback
        self.sp_client = self.spotify_client()
    
    def spotify_client(self):
        scopes = ("user-library-read",
                  "playlist-read-private",
                  "playlist-read-collaborative",
                  "playlist-modify-public",
                  "playlist-modify-private")



        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.callback,
            scope=scopes
        ))
        return sp

    def search_spotify_track_id(self, title, artist, limit:int = 10):
        """Search for a Spotify track ID given a title and artist."""
        results = self.sp_client.search(q=f'track:{title} artist:{artist}', 
                                        limit=limit,
                                        type='track')
        track_id = [x.get('id') for x in results['tracks']['items']]
        return track_id

    def get_user_playlists(self):
        user_playlists = self.sp_client.current_user_playlists(limit=50, offset=0)
        owned_playlists = [{"id":pl['id'], "name":pl['name']} for pl in user_playlists['items'] if pl['owner']['id'] == self.sp_client.current_user()['id']]
        return owned_playlists

    def get_playlist_songs(self, playlist_id)->list:
        """Get a list of Spotify track IDs from a playlist."""
        results = self.sp_client.playlist_tracks(playlist_id)
        song_ids = [song['item']['id'] for song in results.get('items', [])]
        return song_ids
