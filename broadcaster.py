import requests
from requests import ReadTimeout
import time
import spotipy
from get_tokens import spotipy_readiness
from supabase_helper import update_track, assign_role
from album_cover_colors import get_album_colors
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DEVICE_ID = os.getenv("deviceID")

access_token = None
expires_at = None
refresh_token = None

def get_current_track():
    """Fetch the currently playing track from Spotify."""
    global access_token, expires_at, refresh_token
    sp, access_token, expires_at, refresh_token = spotipy_readiness(access_token, refresh_token, expires_at)

    if not sp:
        return None

    try:
        track_info = sp.current_user_playing_track()

        # Initialize the current_playback_device variable
        current_playback_device = None
        try:
            devices = sp.devices().get("devices", [])
            if devices:
                current_playback_device = devices[0]["id"]
        except Exception as e:
            print(f"Error retrieving devices: {e}")

    except ReadTimeout:
        print("Read Timeout Error Occurred. Retrying in 5 seconds...")
        time.sleep(5)
        return get_current_track()
    except Exception as e:
        print(f"Error getting data: {e}. Retrying in 5 seconds...")
        time.sleep(5)
        return get_current_track()

    if track_info and track_info.get("is_playing") and current_playback_device == DEVICE_ID:
        try:
            colors = get_album_colors(track_info["item"]["album"]["images"][0]["url"], False)
        except Exception as e:
            print(f"Error getting album colors: {e}")
            colors = [192, 192, 192]
        return {
            "track_uri": track_info["item"]["uri"],
            "album": track_info["item"]["album"]["name"],
            "artist": track_info["item"]["artists"][0]["name"],
            "song": track_info["item"]["name"],
            "album_cover_url": track_info["item"]["album"]["images"][0]["url"] if track_info["item"]["album"]["images"] else None,
            "color": colors
        }
    return None


def broadcast_track():
    """Continuously check for track changes and send updates."""
    last_track = None
    assign_role("Broadcaster")

    while True:
        track_data = get_current_track()
        
        if track_data and track_data != last_track:
            update_track(track_data)
            last_track = track_data  # Avoid duplicate updates

        time.sleep(2)  # Adjust polling frequency as needed

if __name__ == "__main__":
    broadcast_track()