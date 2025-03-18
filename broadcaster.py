import requests
import time
from spotify_auth import get_spotify_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

WEB_SERVER = os.getenv("WEB_SERVER_URL")

SERVER_URL = str(WEB_SERVER + "/update")  # Change to your actual server

def get_current_track():
    """Fetch the currently playing track from Spotify."""
    sp = get_spotify_client()
    track_info = sp.current_user_playing_track()

    if track_info and track_info.get("is_playing"):
        return {
            "track_name": track_info["item"]["name"],
            "artist": track_info["item"]["artists"][0]["name"],
            "album": track_info["item"]["album"]["name"],
            "track_url": track_info["item"]["external_urls"]["spotify"]
        }
    return None

def broadcast_track():
    """Continuously check for track changes and send updates."""
    last_track = None

    while True:
        track_data = get_current_track()
        
        if track_data and track_data != last_track:
            print(f"Broadcasting: {track_data['track_name']} by {track_data['artist']}")
            requests.post(SERVER_URL, json=track_data)
            last_track = track_data  # Update last track to avoid duplicate updates

        time.sleep(5)  # Adjust polling frequency as needed

if __name__ == "__main__":
    broadcast_track()