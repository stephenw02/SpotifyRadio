from broadcaster import broadcast_track
from listener import listen_for_updates


pi_input = 'broadcast'

if pi_input == 'broadcast':
    try:
        broadcast_track()
    except:
        print("Error Broadcasting")

elif pi_input == "listen":
    try:
        listen_for_updates()
    except:
        print("Error Listening")