import requests
import socketio

SERVER_URL = "http://192.168.0.15:8080/track"  # Change to your actual server


sio = socketio.Client()

@sio.event
def connect():
    print("Connected to server.")

@sio.event
def track_update(data):
    """Handle incoming track updates from the broadcaster."""
    print(f"New Track: {data.get('track_name')} by {data.get('artist')}")

@sio.event
def disconnect():
    print("Disconnected from server.")

# Connect to the relay server
sio.connect(SERVER_URL)

# Keep the script running to listen for updates
sio.wait()