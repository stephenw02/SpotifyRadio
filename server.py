from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

app = Flask(__name__)
CORS(app)  # Allow requests from anywhere
socketio = SocketIO(app, cors_allowed_origins="*")

# Store track info in memory (resets on server restart)
current_track = {}

@app.route('/update', methods=['POST'])
def update_track():
    """Update track info and notify listeners via WebSocket."""
    global current_track
    data = request.json
    current_track = data

    # Send update to all connected listeners
    socketio.emit('track_update', current_track)

    return jsonify({"message": "Track updated successfully"}), 200

@app.route('/track', methods=['GET'])
def get_track():
    """Return the current track info."""
    return jsonify(current_track)

@socketio.on('connect')
def handle_connect():
    """Send the latest track to a new listener when they connect."""
    emit('track_update', current_track)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)