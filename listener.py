import requests
import socketio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

WEB_SERVER = os.getenv("WEB_SERVER_URL")

SERVER_URL = str(WEB_SERVER + "/track")  # Change to your actual server


sio = socketio.Client()

@sio.event
def connect():
    print("Connected to server.")

@sio.event
def track_update(data):
    """Handle incoming track updates from the broadcaster."""
    print(f"New Track: {data.get('track_name')} by {data.get('artist')}")
    # Add code to start playback

@sio.event
def disconnect():
    print("Disconnected from server.")

# Connect to the relay server
sio.connect(SERVER_URL)

# Keep the script running to listen for updates
sio.wait()