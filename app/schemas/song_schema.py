from pydantic import BaseModel
from typing import Optional

class SongInfo(BaseModel):
    spotify_id: str
    reccobeats_id: Optional[str] = None
    title: Optional[str] = None
    artist: Optional[str] = None
    acousticness: Optional[float] = None
    danceability: Optional[float] = None
    energy: Optional[float] = None
    instrumentalness: Optional[float] = None
    key: Optional[int] = None
    liveness: Optional[float] = None
    loudness: Optional[float] = None
    mode: Optional[int] = None
    speechiness: Optional[float] = None
    tempo: Optional[float] = None
    valence: Optional[float] = None
    durationMs: Optional[int] = None
    hype_score: Optional[float] = None
    motivation_score: Optional[float] = None
    energy_score: Optional[float] = None