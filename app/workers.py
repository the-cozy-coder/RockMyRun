import threading
from flask import current_app
from .jobs import jobs
from .services.spotify_service import get_playlist_songs
from .services.song_service import add_songs_to_database
from .services.recommendation_service import process_seeds, KNN_recommendations
from app.database import db

import time

def run_search(app, job_id, playlist_ids, playlists):
    with app.app_context():
        song_spotify_ids = []
        try:
            jobs[job_id]["status"] = "running"
            jobs[job_id]["message"] = "Getting playlists..."

            for pl_id in playlist_ids:
                playlist_info =  next((item for item in playlists if item["id"] == pl_id), None)
                jobs[job_id]["message"] = f"processing {playlist_info.get('name')} playlist..."
                results = get_playlist_songs(pl_id)
                jobs[job_id]["message"] = f"Retrieved {len(results)} results"
                song_spotify_ids.extend(results)

            jobs[job_id]["message"] = "Adding new playlist songs to the Database"
            add_songs_to_database(song_spotify_ids)
            

     
        except Exception as e:
            print(str(e))
            jobs[job_id]["status"] = "error"
            jobs[job_id]["message"] = str(e)

        finally:
            db.session.remove()

def get_recommendations(app, job_id, seeds):
    duration = 30
    with app.app_context():
        jobs[job_id]['message'] = "Processing song requests"
        print("processing song requets")
        try:
            seed_ids = process_seeds(seeds)
            num_recommendations = duration // 2
            seed_recommendations = KNN_recommendations(seed_ids, 
                                                       k=num_recommendations)
            jobs[job_id]['message']= f"Recovered {len(seed_recommendations)} recommendations"
            jobs[job_id]['results']= seed_recommendations
            jobs[job_id]["status"] = "complete"
        except Exception as e:
            print(str(e))
            jobs[job_id]["status"] = "error"
            jobs[job_id]["message"] = str(e)
    
        finally:
            db.session.remove()
            

        # artists = [track.split(' - ')[1] for track in seeds if ' - ' in track]

        # return {
        #     'artists': artists,
        #     'all_songs': seed_recommendations,
        #     'total_results': len(seed_recommendations),
        # }




    
         


def start_processing_playlists(job_id, playlist_ids, playlists):

    app = current_app._get_current_object()

    thread = threading.Thread(
        target=run_search,
        args=(app, job_id, playlist_ids, playlists)
    )

    thread.start()

def start_processing_recommendations(job_id, seeds):

    app = current_app._get_current_object()

    thread = threading.Thread(
        target=get_recommendations,
        args=(app, job_id, seeds)
    )

    thread.start()

