from flask import Flask
from .database import db
from config import Config
import logging


def create_app():

    app = Flask(__name__)
    jobs = {}

    app.config.from_object(Config)
    app.logger.setLevel(logging.INFO)
    app.logger.info("starting app")
    db.init_app(app)

    from .models import Songs
    from .routes import main

    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app



