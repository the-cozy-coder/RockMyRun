from ..models.VibeProfiles import VibeProfile
from .song_service import get_songs_by_spotify_id
from ..database import db
from flask import jsonify


import sqlite3
import json
import random
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.spatial import KDTree

def get_all_vibe_profiles(limit=None):

    query = VibeProfile.query

    if limit:
        query = query.limit(limit)

    return query.all()


def save_vibe_profile(data):
    
    try:
        vibe_profile = VibeProfile(
            name=data.get('name'),
            duration=data.get('duration', 30),
            hype_data=data.get('hype_data'),
            energetic_data=data.get('energetic_data'),
            motivation_data=data.get('motivation_data')
        )

        db.session.add(vibe_profile)
        db.session.commit()

        
        return jsonify({
            'success': True,
            'profile_id': vibe_profile.id
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error saving vibe profile: {e}")

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_vibe_profile(profile_id):
    return VibeProfile.query.get_or_404(profile_id)

def exponential_model(x, a, b):
    return a * np.exp(b * x)

def extrapolate_vibe_curve(time_points, vibe_data):

    cs = CubicSpline(time_points, vibe_data)
    return cs

def generate_playlist_from_vibe(vibe_profile, recommendations):
    """Generate a playlist that matches the vibe profile and favors search-result songs when provided."""

    hype_curve = extrapolate_vibe_curve(np.linspace(0, 1, len(vibe_profile.hype_data)).tolist(), vibe_profile.hype_data)
    energetic_curve = extrapolate_vibe_curve(np.linspace(0, 1, len(vibe_profile.energetic_data)).tolist(), vibe_profile.energetic_data)
    motivation_curve = extrapolate_vibe_curve(np.linspace(0, 1, len(vibe_profile.motivation_data)).tolist(), vibe_profile.motivation_data)

    duration = vibe_profile.duration * 60

    # Get recommended songs
    rows = get_songs_by_spotify_id(recommendations)

    songs = {
            r.spotify_id  : {
            'title': r.title,
            'duration_sec': r.durationMs / 1000,
            'artist': r.artist,
            'hype_score': r.hype_score,  # Suitability for dancing (0.0 to 1.0). Higher values indicate more rhythmically engaging tracks.
            'energy_score': r.energy_score, #Intensity and liveliness (0.0 to 1.0). Higher values indicate more energetic tracks.
            'motivation_score': r.motivation_score, #Overall loudness in decibels (dB). Higher values indicate louder tracks.
            }
        for r in rows
    }
    if not songs:
        return {'name': vibe_profile.name, 'songs': [], 'message': 'No songs in database. Add songs first.'}
    X = [[r.hype_score, r.energy_score, r.motivation_score] for r in rows]
    y = [r.spotify_id for r in rows]
    vibe_tree = KDTree(X)
    
    
    playlist = []
    playlist_duration = 0
    used_song_ids = set()
    
    while playlist_duration < duration:
        current_vibe = [hype_curve(playlist_duration / duration), 
                        energetic_curve(playlist_duration / duration), 
                        motivation_curve(playlist_duration / duration)]
        
        # find the song closest to the currnet vibe
        distances, indices = vibe_tree.query(current_vibe, k=10)
        # make sure that the song hasn't already been used
        for song_i in indices[1:]:
            if y[song_i] not in used_song_ids:
                used_song_ids.add(y[song_i])
                data = songs.get(y[song_i])
                data['start_time'] = round(playlist_duration / 60, 2)
                data['duration'] = round(data['duration_sec'] / 60, 2)
                data['target_vibes'] = {"hype": current_vibe[0],
                                        "energy": current_vibe[1],
                                        "motivation": current_vibe[2]}
                playlist.append(data)
                playlist_duration = playlist_duration + songs.get(y[song_i]).get('duration_sec')
                break
            else:
                continue
        
    
    # title artist bpm energy vibes
    return {
        'name': f"{vibe_profile.name} Playlist",
        'duration': round(playlist_duration/60, 1),
        'songs': playlist,
        'total_songs': len(playlist)
    }
