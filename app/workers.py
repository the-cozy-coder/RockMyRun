import threading
from .jobs import jobs
from .services.spotify_service import get_playlist_songs

import time

def run_search(job_id, playlist_ids, playlists):
    songs = []

    print(playlists)
    try:
        jobs[job_id]["status"] = "running"
        jobs[job_id]["message"] = "Getting playlists..."

        for pl_id in playlist_ids:
            playlist_info =  next((item for item in playlists if item["id"] == pl_id), None)
            jobs[job_id]["message"] = f"processing {playlist_info.get('name')} playlist..."
            results = get_playlist_songs(pl_id)

            for song in results.get('items', []):
                song_info = song['item']
                track_name = song_info['name']
                track_id = song_info['id']
                track_artist = song_info['artists'][0]['name'] if song_info['artists'] else 'Unknown Artist'
                songs.append({
                    'id': track_id,
                    'title': track_name,
                    'artist': track_artist,
                })

          
        jobs[job_id]["message"] = "playlists complete"
        jobs[job_id]["status"] = "complete"

    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["message"] = str(e)
        jobs[job_id]["status"] = "complete"



def start_processing_playlists(job_id, playlist_ids, playlists):

    thread = threading.Thread(
        target=run_search,
        args=(job_id, playlist_ids, playlists)
    )

    thread.start()