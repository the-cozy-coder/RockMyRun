import requests
from flask import Blueprint
from flask import current_app
from flask import Flask, render_template, request, jsonify, session, redirect
from .models.Songs import Song
from .models.VibeProfiles import VibeProfile
from .services.song_service import get_all_songs
from .services.vibe_service import get_all_vibe_profiles
from .services.spotify_service import get_user_playlists
from .workers import start_processing_playlists
from uuid import uuid4
# Dev librariews
import time
from .jobs import jobs


main = Blueprint("main", __name__)

@main.route("/test-song-db")
def test_song_db():

    songs = get_all_songs(limit=50)

    return "<br>".join(
        [
            f"{song.title} - {song.artist} - {song.spotify_id}"
            for song in songs
        ]
    )

@main.route("/test-vibe-db")
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
    user_playlists = []
    try:
        user_playlists = session.get('user_playlists', [])
        if user_playlists is None or len(user_playlists) == 0:
            user_playlists = get_user_playlists()
    
    
    except requests.exceptions.ReadTimeout as e:
        current_app.logger.error(e)

    session['user_playlists'] = user_playlists
    return render_template("index.html", user_playlists=user_playlists)

@main.route("/search", methods = ["POST"])
def search():

    query = request.form["seed_tracks"]
    selected_playlist_ids = request.form.getlist("playlist_ids")

    job_id = str(uuid4())

    jobs[job_id] = {
        "status": "running",
        "results": None
    }

    # print(job_id, selected_playlist_ids, session['user_playlists'])
    # print(jobs)
    start_processing_playlists(job_id, selected_playlist_ids, session['user_playlists'])

    return redirect(f"/searching/{job_id}")

@main.route("/searching/<job_id>")
def searching(job_id):
    print(jobs)
    return render_template(
        "searching.html",
        job_id=job_id
    )

@main.route("/status/<job_id>")
def status(job_id):
    print(jobs[job_id]["status"])
    return {
        "status": jobs[job_id]["status"],
        "message": jobs[job_id]["message"]
    }

@main.route("/results/<job_id>")
def results(job_id):

    return render_template(
        "results.html",
        # results=jobs[job_id]["results"]
        search_results = {"artists": ['artist1', 'artist2', 'artist3']}
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