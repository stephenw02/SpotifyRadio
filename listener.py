import time
from get_tokens import spotipy_readiness
from supabase_helper import get_latest_track, assign_role, get_broadcasters, remove_role
import os
from dotenv import load_dotenv
from switch_position import read_switch
from light_controller import light_blue, light_off

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

    if not sp or not track_uri:
        return

    try:
        # Initialize the current_playback_device variable
        current_playback_device = None
        try:
            devices = sp.devices().get("devices", [])
            #print(devices)
            for device in devices:
                if device.get("name") == "Spotify Radio":
                    current_playback_device = device["id"]
                    break
            if current_playback_device is None:
                print("No active Spotify device found")
        except Exception as e:
            print(f"Error retrieving devices: {e}")

        if current_playback_device == DEVICE_ID:
            sp.start_playback(device_id=DEVICE_ID, uris=[track_uri])
            print(f"▶️ Now playing: {track_uri}")
        else:
            print(f"Device mismatch or not found: Expected {DEVICE_ID}, got {current_playback_device}")

    except Exception as e:
        print(f"Error starting playback: {e}")

def listen_for_updates():
    """Continuously check for the latest track and play it if it changes."""
    last_track_uri = None
    assign_role("Listener")
    prev_light = None

    try:
        # For pi
        while read_switch() == "Listening":
            if get_broadcasters() > 0 and prev_light != "blue": 
                light_blue()
                prev_light = "blue"
            else: 
                if prev_light == None or prev_light == "off":
                    light_blue()
                    prev_light = "blue"
                else:
                    light_off()
                    prev_light = "off"
            try:
                latest_track = get_latest_track()

                if latest_track and latest_track.get("track_uri") != last_track_uri:
                    track_uri = latest_track.get("track_uri")
                    print(f"🎶 New Track: {latest_track.get('song')} by {latest_track.get('artist')}")
                    update_playback(track_uri)
                    last_track_uri = track_uri  # Avoid re-playing the same track

                time.sleep(2)  # Adjust polling frequency as needed

            except Exception as e:
                print(f"Error while listening for updates: {e}")
                time.sleep(5)
        # When no longer broadcasting, remove role
        remove_role()
            
    except:
        # For local
        while True:
            try:
                latest_track = get_latest_track()

                if latest_track and latest_track.get("track_uri") != last_track_uri:
                    track_uri = latest_track.get("track_uri")
                    print(f"🎶 New Track: {latest_track.get('song')} by {latest_track.get('artist')}")
                    update_playback(track_uri)
                    last_track_uri = track_uri  # Avoid re-playing the same track

                time.sleep(2)  # Adjust polling frequency as needed

            except Exception as e:
                print(f"Error while listening for updates: {e}")
                time.sleep(5)

if __name__ == "__main__":
    listen_for_updates()