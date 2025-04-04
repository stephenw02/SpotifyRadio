from broadcaster import broadcast_track
from supabase_helper import get_broadcasters
from listener import listen_for_updates
from switch_position import read_switch
from light_controller import light_red, light_blue, light_white, light_off
from pi_setup import handle_config
import time

prev_light = None

is_configured = handle_config()

while is_configured == False:
    light_white()
    time.sleep(1)
    light_red()
    time.sleep(1)



while is_configured==True:
    pi_input = read_switch()
    broadcast_count = get_broadcasters()

    if pi_input == 'Broadcasting':
        try:
            broadcast_track()
        except:
            print("Error Broadcasting")

    elif pi_input == "Listening":
        try:
            listen_for_updates()
        except:
            print("Error Listening")

    elif pi_input == "Off" and broadcast_count == 0:
        light_off()

    elif pi_input == "Off" and broadcast_count > 0:
        if prev_light == None or prev_light == "off":
            light_white()
            prev_light = "white"
        else:
            light_off()
            prev_light = "off"

