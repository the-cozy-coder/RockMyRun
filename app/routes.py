import requests
from flask import Blueprint
from flask import current_app
from flask import Flask, render_template, request, jsonify, session, redirect
from .models.Songs import Song
from .models.VibeProfiles import VibeProfile
from .services.song_service import get_all_songs, get_result_data
from .services.vibe_service import (get_all_vibe_profiles, save_vibe_profile, 
                                    get_vibe_profile, generate_playlist_from_vibe)
from .services.spotify_service import get_user_playlists
from .services.spotify_client import get_spotify_oauth
from .workers import start_search_pipeline, start_vibe_pipeline
from uuid import uuid4
# Dev librariews
import time
from .jobs import jobs


main = Blueprint("main", __name__)


@main.route("/spotify/login")
def spotify_login():

    spotify_oauth = get_spotify_oauth()

    authorization_url = spotify_oauth.get_authorize_url()

    return redirect(authorization_url)

@main.route("/callback")
def spotify_callback():
    spotify_oauth = get_spotify_oauth()

    code = request.args.get("code")

    if not code:
        return "No authorization code received", 400

    token_info = spotify_oauth.get_access_token(code)

    return f"Successfully connected to Spotify!"



@main.route("/song-db")
def test_song_db():

    songs = get_all_songs(limit=50)

    return "<br>".join(
        [
            f"{song.title} - {song.artist} - {song.spotify_id} - {song.hype_score} - {song.reccobeats_id}"
            for song in songs
        ]
    )

@main.route("/vibe-db")
def test_vibe_db():

    vibes = get_all_vibe_profiles(limit=5)

    return "<br>".join(
        [
            f"{vibe.id} - {vibe.duration} - {vibe.hype_data}"
            for vibe in vibes
        ]
    )

@main.route("/")
def home():
    # user_playlists = []
    # try:
    #     user_playlists = session.get('user_playlists', [])
    #     if user_playlists is None or len(user_playlists) == 0:
    #         user_playlists = get_user_playlists()
    
    
    # except requests.exceptions.ReadTimeout as e:
    #     current_app.logger.error(e)

    # session['user_playlists'] = user_playlists
    # return render_template("index.html", user_playlists=user_playlists)
    user_playlists = session.get(
        "user_playlists",
        []
    )

    return render_template(
        "index.html",
        user_playlists=user_playlists
    )

@main.route("/search", methods = ["POST"])
def search():

    seeds = request.form["seed_tracks"]
    playlist_ids = request.form.getlist("playlist_ids")

    job_id = str(uuid4())

    jobs[job_id] = {
        "status": "running",
        "results": None
    }

    start_search_pipeline(job_id, playlist_ids, seeds)

    return redirect(f"/searching/{job_id}")

@main.route("/searching/<job_id>")
def searching(job_id):
    return render_template(
        "searching.html",
        job_id=job_id
    )

@main.route("/status/<job_id>")
def status(job_id):
    return {
        "status": jobs[job_id]["status"],
        "message": jobs[job_id]["message"]
    }

@main.route("/results/<job_id>")
def results(job_id):

    search_results = {
        'artists': ['artist1aa', 'artist2aaa', 'artist3aaa'],
        'all_songs': get_result_data(jobs[job_id]["results"]),
        'total_results': len(jobs[job_id]["results"]),
    }

    return render_template(
        "results.html",
        search_results = search_results
    )

@main.route("/error/<job_id>")
def error(job_id):

    job = jobs.get(job_id)

    if not job:
        return "Job not found", 404

    return render_template(
        "error.html",
        error_message=job.get("message", "An unknown error occurred.")
    )


@main.route('/save_vibe_profile', methods=['POST'])
def save_vibe_profile_route():
    """Persist a vibe profile sent by the front-end and return the new profile id."""
    data = request.get_json()
    response = save_vibe_profile(data)
    return response


@main.route("/generate_playlist/<int:profile_id>", methods=['GET', 'POST'])
def VibeSearch(profile_id):

    vibe_profile = get_vibe_profile(profile_id)

    seed_tracks = request.args.get("seed_tracks", "")
    playlist_ids = request.args.getlist("playlist_ids")

    job_id = str(uuid4())
    
    jobs[job_id] = {
        "status": "running",
        "results": None
    }
    
    start_vibe_pipeline(job_id, playlist_ids, seed_tracks, vibe_profile)

    return redirect(f"/searching/{job_id}")

@main.route("/playlist/<job_id>")
def playlist(job_id):

    playlist = jobs[job_id]['playlist']
    return render_template('playlist.html', playlist=playlist)