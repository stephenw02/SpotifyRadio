import requests
from get_tokens import spotipy_readiness
import socketio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

WEB_SERVER = os.getenv("WEB_SERVER_URL")

SERVER_URL = str(WEB_SERVER + "/track")  # Change to your actual server

DEVICE_ID = os.getenv("deviceID")

access_token = None
expires_at = None
refresh_token = None

sio = socketio.Client()

def update_playback(track_uri):
    """Update currently playing to new track from broadcaster"""
    global access_token, expires_at, refresh_token
    sp, access_token, expires_at, refresh_token = spotipy_readiness(access_token, refresh_token, expires_at)
    sp.start_playback(device_id=DEVICE_ID, uris=[track_uri])

@sio.event
def connect():
    print("Connected to server.")

@sio.event
def track_update(data):
    """Handle incoming track updates from the broadcaster."""
    print(f"New Track: {data.get('track_name')} by {data.get('artist')}")
    track_uri = data.get('track_uri')
    print(track_uri)
    update_playback(track_uri)

@sio.event
def disconnect():
    print("Disconnected from server.")

# Connect to the relay server
sio.connect(SERVER_URL)

# Keep the script running to listen for updates
sio.wait()