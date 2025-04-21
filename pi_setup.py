import json
import os
import time
import subprocess
import socket

USB_MOUNT_PATH = "/media/stephenw02"

def find_config_file():
    for root, dirs, files in os.walk(USB_MOUNT_PATH):
        for file in files:
            if file == "config.json":
                return os.path.join(root, file)
    return None

def apply_wifi_settings(ssid, password):
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        connected=True
    except:
        connected=False
    if connected==True:
        return True
    else:
        wpa_supplicant_path = "/etc/wpa_supplicant/wpa_supplicant.conf"
        new_config = f'''network={{ssid="{ssid}"psk="{password}"}}'''
        with open(wpa_supplicant_path, "a") as f:
            f.write(new_config)
        print("📶 WiFi config updated. Rebooting to apply settings...")
        os.system("sudo reboot")

def configure_raspotify():
    config_path = "/etc/raspotify/conf"
    if not os.path.exists(config_path):
        print("❌ Raspotify config not found. Is it installed?")
        return False

    with open(config_path, "r") as f:
        lines = f.readlines()

    # Modify or insert USERNAME and PASSWORD
    new_lines = []
    for line in lines:
        if line.startswith("#LIBRESPOT_NAME=") or line.startswith("LIBRESPOT_NAME="):
            new_lines.append('LIBRESPOT_NAME="Spotify Radio"\n')
        elif line.startswith("#LIBRESPOT_USERNAME=") or line.startswith("LIBRESPOT_USERNAME="):
            new_lines.append(f'#LIBRESPOT_USERNAME=""\n')
        elif line.startswith("#LIBRESPOT_PASSWORD=") or line.startswith("LIBRESPOT_PASSWORD="):
            new_lines.append(f'#LIBRESPOT_PASSWORD=""\n')
        else:
            new_lines.append(line)

    with open(config_path, "w") as f:
        f.writelines(new_lines)

    print("🎵 Raspotify credentials updated. Restarting service...")
    subprocess.run(["sudo", "systemctl", "restart", "raspotify"])
    return True

def handle_config():
    config_file = find_config_file()
    if not config_file:
        print("❌ No config.json file found on USB.")
        return False

    with open(config_file, "r") as f:
        data = json.load(f)

    if "wifi_ssid" in data and "wifi_password" in data:
        wifi_set = apply_wifi_settings(data["wifi_ssid"], data["wifi_password"])

    raspotify_set = configure_raspotify()

    if raspotify_set==True and wifi_set==True:
        return True
    else:
        return False

if __name__ == "__main__":
    time.sleep(5)  # Give time for USB to mount
    handle_config()