from ..database import db
from datetime import datetime, timezone

class User(db.Model):

    __tablename__ = "user"
    id = db.Column(db.Integar, primary_key = True)
    spotify_id = db.Column(db.String, unique=True, nullable=False)
    display_name = db.Column(db.String)
    access_token = db.Column(db.String)
    refresh_token = db.Column(db.String)
    token_expires_at = db.Column(db.DateTime)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
