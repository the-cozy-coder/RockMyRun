from ..database import db
from ..models.Songs import Song
from .reccobeats_service import get_track_info, get_track_audio_details
from pprint import pprint
from ..schemas.song_schema import SongInfo
from flask import current_app
from sqlalchemy import func

def get_random_song_id():
    song = (
        Song.query
        .with_entities(Song.spotify_id)
        .filter(Song.reccobeats_id.isnot(None))
        .order_by(func.random())
        .first()
    )

    return song.spotify_id if song else None


def get_all_songs(limit=None):

    query = Song.query

    if limit:
        query = query.limit(limit)

    return query.all()

def get_songs_by_spotify_id(sids: list[str]) -> list[Song]:
    """Get songs from local database matching Spotify IDs."""

    if not sids:
        return []

    songs = (
        Song.query
        .filter(Song.spotify_id.in_(sids))
        .all()
    )

    return songs

def filter_for_audio_data(sids: list[str]) -> list[Song]:
    if not sids:
        return []

    songs = db.session.scalars(
        db.select(Song.spotify_id)
        .where(
            Song.spotify_id.in_(sids),
            Song.reccobeats_id.isnot(None)
        )
    ).all()
    current_app.logger.info(f"seeds data = {songs}")
    return songs

def get_song_by_title(title: str) -> Song | None:
    """Get first song from local database matching title."""
    return Song.query.filter_by(
        title=title
    ).first()

def get_songs_by_title_and_artist(title: str, artist: str) -> Song:
    return Song.query.filter(
        Song.title == title,
        Song.artist == artist
    ).first()

def save_song(SongInfo):
    """Save a song if it does not already exist."""

    existing_song = Song.query.filter_by(
        spotify_id=SongInfo.spotify_id
    ).first()

    if existing_song:
        return existing_song

    song = Song(**SongInfo.model_dump())
    db.session.merge(song)
    db.session.commit()

def save_songs(songs: list):
    db_songs = [
        Song(**song.model_dump())
        for song in songs
    ]

    db.session.add_all(db_songs)
    current_app.logger.info(f"Saved {len(songs)} songs to the database")
    db.session.commit()

def normalize_to_100(numbers):
    total = sum(numbers)
    if total == 0:
        raise ValueError("The sum of the list cannot be zero.")
    return [(num / total) * 100 for num in numbers]

def calc_vibe_data(song_info):

    '''Generates Vibe scores for each song.  For now we are just using a rule based huristic.
    TODO: develop user scoring page to create a labeled dataset, 
        then create a learned algorithm for each vibe 
    '''
    vibe_data = {}
    for k, v in song_info.items():
        loudness_norm = (v.get('loudness') + 60) / 60
        tempo_norm = min(v.get('tempo'), 200) / 200  

        hype_score = (0.50 * v.get('energy') +
                        0.30 * v.get('danceability') +
                        0.20 * v.get('valence')
        )

        motivation_score = (
            0.45 * v.get('energy') +
            0.25 * loudness_norm +
            0.30 * tempo_norm
        )
        energy_score = (
            v.get('energy') *
            loudness_norm *
            (0.5 + tempo_norm / 2)
        )
        norm_scores = normalize_to_100([hype_score, motivation_score, energy_score])
        vibe_data[k] = {'hype_score': round(norm_scores[0], 2),
            'motivation_score': round(norm_scores[1], 2),
            'energy_score': round(norm_scores[2], 2)}
    return vibe_data
    
def filter_seeds(sids: list):
    '''
    Returns the first id that has reccobeats data
    '''
    song_info = get_track_info(tuple(sids))
    sids = [x.get('spotify_id') for x in song_info]
    current_app.logger.info(f"filtered sids = {sids}")
    return sids[0]



def get_complete_song_data(sids:list) -> list[SongInfo]:
    complete_data = []
    existing_ids = [song.spotify_id for song in get_songs_by_spotify_id(sids)]
    current_app.logger.info(f"songs already in the database = {existing_ids}")
    songs_to_add = tuple(set(sids) - set(existing_ids))
    if len(songs_to_add) == 0:
        return {}


    song_info = get_track_info(songs_to_add)
    audio_info = get_track_audio_details(songs_to_add)
    

    song_info_dict = {x.get("spotify_id"): x for x in song_info}
    audio_info_dict = {x.get("href").split('/')[-1]: x for x in audio_info}
    vibe_data_dict = calc_vibe_data(audio_info_dict)
    complete_data = [SongInfo(**{**{"spotify_id": key, "title": f"unknownTitle-{key}", 'artist': 'artist unknown'},
                                 **song_info_dict.get(key, {}),
                                 **audio_info_dict.get(key, {}), 
                                 **vibe_data_dict.get(key, {}),
                                 }) for key in songs_to_add]

    return complete_data

def add_songs_to_database(spotify_ids: list):
    current_app.logger.info(f'Adding songs to database {spotify_ids}')
    song_data = get_complete_song_data(spotify_ids)
    current_app.logger.info("retrieved song data")
    save_songs(song_data)

def get_all_audio_data():
    songs = (
        Song.query
        .with_entities(
            Song.spotify_id,
            Song.acousticness,
            Song.danceability,
            Song.energy,
            Song.instrumentalness,
            Song.liveness,
            Song.loudness,
            Song.mode,
            Song.speechiness,
            Song.tempo,
            Song.valence,
        )
        .filter(
            Song.reccobeats_id.isnot(None)
        )
        .all()
    )

    
    return songs


def get_result_data(sids):
    print(sids)
    songs = (
        Song.query
        .with_entities(
            Song.artist,
            Song.title,
        )
        .filter(Song.spotify_id.in_(sids))
        .all()
    )

    return [
        {
            "artist": song.artist,
            "title": song.title
        }
        for song in songs
    ]

