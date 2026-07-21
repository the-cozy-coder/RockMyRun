from flask import Flask
from .database import db
from config import Config


def create_app():

    app = Flask(__name__)
    jobs = {}

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///songs.db"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    app.config.from_object(Config)

    from .models import Songs
    from .routes import main

    app.register_blueprint(main)

    return app

