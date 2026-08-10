from .spotify_client import SpotifyClient
from ..models.User import User
from datetime import datetime
from ..database import db


from flask import current_app

def query_user(token_info):
    current_app.logger.info(f"USER CLASS: {User}")
    current_app.logger.info(f"USER TYPE: {type(User)}")
    spotify = SpotifyClient(token_info["access_token"])
    spotify_user = spotify.sp_client.current_user()

    spotify_id = spotify_user.get('id')
    display_name = spotify_user.get('display_name')

    user = User.query.filter_by(
        spotify_id = spotify_id
    ).first()

    if user is None:
        user = User(
            spotify_id = spotify_id,
            display_name = display_name,
            access_token = token_info.get("access_token"),
            refresh_token = token_info.get("refresh_token"),
            token_expires_at = datetime.fromtimestamp(
                token_info.get("expires_at")
            )
        )

        db.session.add(user)
    else:
        user.access_token = token_info['access_token']
        user.display_name = display_name
        if token_info.get("refresh_token"):
            user.refresh_token = token_info.get("refresh_token")

        user.token_expires_at = datetime.fromtimestamp(
            token_info.get("expires_at")
        )

    db.session.commit()


    current_app.logger.info(
        f"USER TYPE: {type(user)}, USER: {user}"
    )
    return user.id