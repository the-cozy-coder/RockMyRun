from flask import Flask
from .database import db
from config import Config


def create_app():

    app = Flask(__name__)
    jobs = {}

    app.config.from_object(Config)

    db.init_app(app)

    from .models import Songs
    from .routes import main

    app.register_blueprint(main)

    return app



