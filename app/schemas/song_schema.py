from pydantic import BaseModel
from typing import Optional

class SongInfo(BaseModel):
    spotify_id: str
    reccobeats_id: Optional[str]
    title: Optional[str]
    artist: Optional[str]
    acousticness: Optional[float]
    danceability: Optional[float]
    energy: Optional[float]
    instrumentalness: Optional[float]
    key: Optional[int]
    liveness: Optional[float]
    loudness: Optional[float]
    mode: Optional[int]
    speechiness: Optional[float]
    tempo: Optional[float]
    valence: Optional[float]
    durationMs: Optional[int]
    hype_score: Optional[float]
    motivation_score: Optional[float]
    energy_score: Optional[float]