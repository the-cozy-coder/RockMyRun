from ..database import db
from ..models.Songs import Song
from .reccobeats_service import get_track_info, get_track_audio_details


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

def get_complete_song_data(sids:list):
    existing_ids = [song.spotify_id for song in get_songs_by_spotify_id(sids)]
    songs_to_add = tuple(set(sids) - set(existing_ids))
    if len(songs_to_add) == 0:
        return {}

    song_info = get_track_info(songs_to_add)
    audio_info = get_track_audio_details(songs_to_add)

    song_info_dict = {x.get("href").split('/')[-1]: x for x in song_info}
    audio_info_dict = {x.get("href").split('/')[-1]: x for x in audio_info}

    complete_data = {
        key: {**song_info_dict.get(key, {}), **audio_info_dict.get(key, {})}
        for key in songs_to_add
    }
    return complete_data
            
def add_songs_to_database(spotify_ids: tuple):
    song_data = get_complete_song_data(spotify_ids)
    # TODO : process vide values
    # TODO: Create song objects
    # TODO: add songs to the database
    return 10

