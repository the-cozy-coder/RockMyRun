from ..database import db

class VibeProfile(db.Model):
    __tablename__ = "vibe_profiles"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String, nullable=False)

    duration = db.Column(
        db.Integer,
        default=30
    )

    hype_data = db.Column(db.JSON)
    energetic_data = db.Column(db.JSON)
    motivation_data = db.Column(db.JSON)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )