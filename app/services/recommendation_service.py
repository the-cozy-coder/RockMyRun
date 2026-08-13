from .song_service import (get_songs_by_title_and_artist, 
                           get_song_by_title, 
                           add_songs_to_database,
                           filter_for_audio_data,
                           get_all_audio_data)
from .spotify_service import get_spotify_track_id
from scipy.spatial import KDTree
import sqlite3
import numpy as np
from flask import current_app

client = None

def process_seeds(user_id, seeds):
    current_app.logger.info(f'processing seeds user id {user_id}')
    current_app.logger.info(f'processing seeds list {seeds}')
    spotify = None
    seed_tracks = [track.strip() for track in seeds.split(',') if track.strip()]
    # First see if the seed track exists in the database
    seed_track_sids = []
    new_sids = []
    for track in seed_tracks:
        title = track.split('-')[0].strip()
        artist = track.split('-')[1].strip()
        song = get_songs_by_title_and_artist(title, artist)
        if song:
            sid = song.spotify_id
        else:
            #If the song by the selected artist isn't in the database try to find 
            # the same song by a different artist
            # TODO: think about this.
            song = get_song_by_title(title)
            if song:
                sid = song.spotify_id
            else:
                sid, spotify = get_spotify_track_id(user_id, title, artist, spotify)
                new_sids.extend(sid)
        if sid is not None:
            sid = sid if isinstance(sid, list) else [sid]
            seed_track_sids.extend(sid)
    # Add seed tracks to the database (will only add tracks that are new)
    add_songs_to_database(new_sids)
    return seed_track_sids
        
def KNN_recommendations(seed_track_sids, k=10):
    """Get recommendations based on seed tracks.""" 
    
    usable_seeds = filter_for_audio_data(seed_track_sids)
    current_app.logger.info(f"Using the following usable seeds:  {usable_seeds}")
    if len(usable_seeds) == 0:
        return []  
     

    songs = get_all_audio_data()
    if k+1 > len(songs):
        k = len(songs) - 1
    current_app.logger.info(f"retrieved {len(songs)} audio data")
    current_app.logger.info(f"retrieved all audio data example - {songs[0:2]}")

    X = [song[1:] for song in songs]
    y = [song[0] for song in songs]

    tree = KDTree(X)
    query_points = [song[1:] for song in songs if song[0] in usable_seeds]
    current_app.logger.info(f"query points = {query_points}")
    seed_recommendations = []
    for query_point in query_points:
        _, indices = tree.query(query_point, k=k+1)
        current_app.logger.info(f"recommendation indices = {indices}")
        seed_recommendations.extend([y[i] for i in indices[1:]])
    return list(set(seed_recommendations))

     












      