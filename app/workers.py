import threading
from flask import current_app
from .jobs import jobs
from .services.spotify_service import get_playlist_songs
from .services.song_service import add_songs_to_database
from .services.recommendation_service import process_seeds, KNN_recommendations
from .services.vibe_service import generate_playlist_from_vibe
from app.database import db

import time

def run_search(app, job_id, playlist_ids):
    with app.app_context():
        song_spotify_ids = []
        jobs[job_id]["status"] = "running"
        jobs[job_id]["message"] = "Getting playlists..."
        current_app.logger.info(f'Getting Playlists - user id = {jobs[job_id]['user_id']}')
        current_app.logger.info(f'Getting Playlists - playlists = {playlist_ids}')

        for pl_id in playlist_ids:
            current_app.logger.info(f"Getting playlist tracks for track {pl_id}")
            results = get_playlist_songs(jobs[job_id]['user_id'], pl_id)
            jobs[job_id]["message"] = f"Retrieved {len(results)} results"
            song_spotify_ids.extend(results)

        jobs[job_id]["message"] = "Adding new playlist songs to the Database"
        current_app.logger.info("Adding new playlist songs to the Database")
        add_songs_to_database(song_spotify_ids)
        current_app.logger.info(f"Added {len(song_spotify_ids)} songs")

def get_recommendations(app, job_id, seeds, duration: int = 30, isVibe = False):
    with app.app_context():
        jobs[job_id]['message'] = "Processing song requests"
        seed_ids, search_crit = process_seeds(jobs[job_id]['user_id'], seeds)
        if len(seed_ids) == 0:
            raise Exception("""None of your seed tracks were found in Spotify.\n
                                 Please check your spelling and try again.""")
        num_recommendations = duration // 2
        seed_recommendations = KNN_recommendations(seed_ids, 
                                                    k=num_recommendations)
        jobs[job_id]['message']= f"Recovered {len(seed_recommendations)} recommendations"
        if not isVibe: 
            jobs[job_id]["status"] = "complete_search"
        else:
            jobs[job_id]["status"] = "genrating Vibe playlist"
    return seed_recommendations, search_crit
            
def get_playlist(app, job_id, vibe_profile, recommendations):
    with app.app_context():
        jobs[job_id]['message'] = "Processing vibe_playlist"
        playlist = generate_playlist_from_vibe(vibe_profile, recommendations)
        jobs[job_id]["status"] = "complete_vibe"
        return playlist
  
def start_search_pipeline(
    job_id,
    playlist_ids,
    seeds
):
    app = current_app._get_current_object()

    thread = threading.Thread(
        target=run_search_pipeline,
        args=(
            app,
            job_id,
            playlist_ids,
            seeds
        )
    )

    thread.start()

def run_search_pipeline(
    app,
    job_id,
    playlist_ids,
    seeds,
):
    with app.app_context():
        try:
            jobs[job_id]["status"] = "running"

            # STEP 1
            run_search(
                app,
                job_id,
                playlist_ids,
            )

            # STEP 2
            recommendations,search_criteria = get_recommendations(
                app,
                job_id,
                seeds,
                duration = 30
            )

            jobs[job_id]["search_criteria"] = search_criteria
            jobs[job_id]["results"] = recommendations
            jobs[job_id]["status"] = "complete_search"
            jobs[job_id]["message"] = "Playlist generated!"
            current_app.logger.info(f"final jobs[job_id] - {jobs[job_id]}")


        except Exception as e:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["message"] = str(e)

        finally:
            db.session.remove()

def start_vibe_pipeline(
    job_id,
    playlist_ids,
    seeds,
    vibe_profile
):
    app = current_app._get_current_object()


    thread = threading.Thread(
        target=run_vibe_pipeline,
        args=(
            app,
            job_id,
            playlist_ids,
            seeds,
            vibe_profile
        )
    )

    thread.start()

def run_vibe_pipeline(
    app,
    job_id,
    playlist_ids,
    seeds,
    vibe_profile
):
    with app.app_context():
        try:
            jobs[job_id]["status"] = "running"

            # STEP 1
            current_app.logger.info(f'run search - vibe profile {vibe_profile}')
            run_search(
                app,
                job_id,
                playlist_ids,
            )

            # STEP 2
            current_app.logger.info(f'get recommendations - vibe profile {vibe_profile}')
            recommendations, search_criteria = get_recommendations(
                app,
                job_id,
                seeds,
                vibe_profile.duration
            )

            # STEP 3
            current_app.logger.info(f'get playlist - vibe profile {vibe_profile}')
            playlist = get_playlist(
                app,
                job_id,
                vibe_profile,
                recommendations
            )
            jobs[job_id]["search_criteria"] = search_criteria
            jobs[job_id]["playlist"] = playlist
            jobs[job_id]["status"] = "complete_vibe"
            jobs[job_id]["message"] = "Playlist generated!"

        except Exception as e:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["message"] = str(e)

        finally:
            db.session.remove()