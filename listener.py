import time
from get_tokens import spotipy_readiness
from supabase_helper import get_latest_track  # Import the function to fetch latest track
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DEVICE_ID = os.getenv("deviceID")

access_token = None
expires_at = None
refresh_token = None

def update_playback(track_uri):
    """Update currently playing to new track from the latest track in Supabase"""
    global access_token, expires_at, refresh_token
    sp, access_token, expires_at, refresh_token = spotipy_readiness(access_token, refresh_token, expires_at)

    if sp and track_uri:
        sp.start_playback(device_id=DEVICE_ID, uris=[track_uri])
        print(f"▶️ Now playing: {track_uri}")

def listen_for_updates():
    """Continuously check for the latest track and play it if it changes."""
    last_track_uri = None

    while True:
        latest_track = get_latest_track()

        if latest_track and latest_track.get("track_uri") != last_track_uri:
            track_uri = latest_track.get("track_uri")
            print(f"🎶 New Track: {latest_track.get('song')} by {latest_track.get('artist')}")
            update_playback(track_uri)
            last_track_uri = track_uri  # Avoid re-playing the same track

        time.sleep(1)  # Adjust polling frequency as needed

if __name__ == "__main__":
    listen_for_updates()