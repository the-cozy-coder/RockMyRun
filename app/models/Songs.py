from ..database import db

class Song(db.Model):
    __tablename__ = "songs"

    spotify_id = db.Column(db.String, primary_key=True)
    reccobeats_id = db.Column(db.String)

    title = db.Column(db.String, nullable=False)
    artist = db.Column(db.String, nullable=False)

    acousticness = db.Column(db.Float)
    danceability = db.Column(db.Float)
    energy = db.Column(db.Float)
    instrumentalness = db.Column(db.Float)
    key = db.Column(db.Integer)
    liveness = db.Column(db.Float)
    loudness = db.Column(db.Float)
    mode = db.Column(db.Integer)
    speechiness = db.Column(db.Float)
    tempo = db.Column(db.Float)
    valence = db.Column(db.Float)

    durationMs = db.Column(db.Integer)

    hype_score = db.Column(db.Float)
    energy_score = db.Column(db.Float)
    motivation_score = db.Column(db.Float)

    __table_args__ = (
        db.UniqueConstraint(
            "title",
            "artist",
            name="uq_song_title_artist"
        ),
    )
