from .spotify_client import SpotifyClient, get_spotify_oauth
from ..models.User import User
from datetime import datetime
from ..database import db


from flask import current_app
from datetime import datetime, timezone

def get_all_users(limit=None):

    query = User.query

    if limit:
        query = query.limit(limit)

    return query.all()


def query_user(token_info):
    spotify = SpotifyClient(token_info["access_token"])
    spotify_user = spotify.sp_client.current_user()

    spotify_id = spotify_user.get('id')
    display_name = spotify_user.get('display_name')

    current_app.logger.info(
        f"Access token length: {len(token_info['access_token'])}"
    )

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
                token_info.get("expires_at"),
                tz=timezone.utc

            )
        )

        db.session.add(user)
    else:
        user.access_token = token_info['access_token']
        user.display_name = display_name
        if token_info.get("refresh_token"):
            user.refresh_token = token_info.get("refresh_token")

        user.token_expires_at = datetime.fromtimestamp(
            token_info.get("expires_at"),
            tz=timezone.utc
        )

    db.session.commit()


    current_app.logger.info(
        f"USER TYPE: {type(user)}, USER: {user}"
    )
    return user.id

def get_valid_access_token(user):
    current_app.logger.info(
            f"user token expires at {user.token_expires_at.replace(tzinfo=timezone.utc)}\n"
            f"now =  {datetime.now(timezone.utc)}\n"
        )

    if (
        user.token_expires_at is not None and
        user.token_expires_at.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc)
    ):
        current_app.logger.info(
            f"Refreshing Spotify token for {user.spotify_id}"
        )
        spotify_oauth = get_spotify_oauth()

        token_info = spotify_oauth.refresh_access_token(
            user.refresh_token
        )

        user.access_token = token_info["access_token"]
        user.token_expires_at = datetime.fromtimestamp(
            token_info["expires_at"],
            tz=timezone.utc
        )

        db.session.commit()

        return user.access_token
    return user.access_token
