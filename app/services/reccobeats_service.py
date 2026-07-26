from functools import lru_cache
import requests

from ..models.Songs import Song

from pprint import pprint


HTTP_TIMEOUT = (2, 5)
REQUEST_SESSION = requests.Session()

def format_track_string(spotify_ids: list, batch_size: int = 30) -> str:
    track_strings = []
    track_batches = [spotify_ids[i:i + batch_size] for i in range(0, len(spotify_ids), batch_size)]
    for batch_ids in track_batches:
        if len(batch_ids) == 0:
            track_string = batch_ids[0]
        else:
            track_string = "&ids=".join(batch_ids)
        track_strings.append(track_string)
    return track_strings

@lru_cache(maxsize=2000)
def get_track_info(spotify_ids: tuple[str])->dict:
    """
    Retrieve track metadata from ReccoBeats for a list of Spotify track IDs.

    This function queries the ReccoBeats track endpoint using batches of
    Spotify IDs and returns the associated track information. Results are
    cached to reduce duplicate API requests for previously requested tracks.

    Args:
        spotify_ids (tuple): A tuple of Spotify track IDs.

    Returns:
        list[dict]: A list of dictionaries containing track metadata returned
        by the ReccoBeats API.

    Raises:
        requests.HTTPError: If the ReccoBeats API request returns an HTTP error.
        requests.Timeout: If the API request exceeds the configured timeout.
        requests.RequestException: For other request-related failures.

    Example:
        >>> tracks = get_track_info(["4iV5W9uYEdYUVa79Axb7Rh"])
        >>> tracks[0]["title"]
        'Something Just Like This'
    """
    song_data = []
    for track_string in format_track_string(list(spotify_ids)):
        url = "https://api.reccobeats.com/v1/track?ids=" + track_string
        headers = {"Accept": "application/json"}
        response = REQUEST_SESSION.get(url, headers=headers, timeout=HTTP_TIMEOUT)
        content = response.json().get('content', [])


        for item in content:
        # Error-proof artist extraction
            artists = item.get('artists')
            if artists and isinstance(artists, list) and len(artists) > 0:
                artist_name = artists[0].get('name', 'artist unknown')
            else:
                artist_name = 'artist unknown'

            song_data.append({"title": item['trackTitle'],
                              "artist": artist_name,
                              'durationMs': item.get('durationMs', 0),
                              "reccobeats_id": item.get('id'),
                              "spotify_id": item.get('href', '').split('/')[-1]
                            })
        response.raise_for_status()
    return song_data

@lru_cache(maxsize=2000)
def get_track_audio_details(spotify_ids: tuple[str]) -> dict:
    """
    Retrieve audio feature information from ReccoBeats for Spotify tracks.

    This function queries the ReccoBeats audio-features endpoint to retrieve
    acoustic characteristics for the provided Spotify track IDs. Results are
    cached to minimize repeated API calls for identical requests.

    Args:
        spotify_ids (tuple): A tuple of Spotify track IDs.

    Returns:
        list[dict]: A list of dictionaries containing audio feature data,
        including attributes such as tempo, energy, danceability, valence,
        acousticness, and other track-level metrics.

    Raises:
        requests.HTTPError: If the ReccoBeats API request returns an HTTP error.
        requests.Timeout: If the API request exceeds the configured timeout.
        requests.RequestException: For other request-related failures.

    Example:
        >>> features = get_track_audio_details(["4iV5W9uYEdYUVa79Axb7Rh"])
        >>> features[0]["energy"]
        0.82
    """    
    content = []
    for track_string in format_track_string(list(spotify_ids)):
        url = "https://api.reccobeats.com/v1/audio-features?ids=" + track_string
        headers = {"Accept": "application/json"}

        response = REQUEST_SESSION.get(url, headers=headers, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        content.extend(response.json().get("content", []))
    return content











    # if not spotify_id:
    #     return Song_info(**_build_empty_song_info(None, []))

    # attribs_to_keep = [
    #     "acousticness",
    #     "energy",
    #     "danceability",
    #     "instrumentalness",
    #     "key",
    #     "liveness",
    #     "loudness",
    #     "mode",
    #     "speechiness",
    #     "tempo",
    #     "valence",
    # ]



    # if len(content) == 0:
    #     return Song_info(**_build_empty_song_info(spotify_id, attribs_to_keep))

    # item = content[0]
    # artists = item.get("artists")
    # artist_name = artists[0].get("name", "artist unknown") if artists and isinstance(artists, list) and len(artists) > 0 else "artist unknown"

    # song_info = {
    #     "title": item.get("trackTitle", "unknown"),
    #     "artist": artist_name,
    #     "durationMs": item.get("durationMs", 0),
    #     "reccobeats_id": item.get("id"),
    #     "spotify_id": item.get("href", "").split("/")[-1] or spotify_id,
    # }

    # song_details = get_reccobeats_track_info(song_info.get("reccobeats_id"))
    # song_info.update({x: song_details.get(x, None) for x in attribs_to_keep})
    # vibe_data = calculate_vibe_data(song_info)
    # song_info.update(vibe_data)
    # return Song_info(**song_info)