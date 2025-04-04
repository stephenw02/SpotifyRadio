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

def configure_raspotify(username, password):
    config_path = "/etc/raspotify/conf"
    if not os.path.exists(config_path):
        print("❌ Raspotify config not found. Is it installed?")
        return False

    with open(config_path, "r") as f:
        lines = f.readlines()

    # Modify or insert USERNAME and PASSWORD
    new_lines = []
    for line in lines:
        if line.startswith("#DEVICE_NAME="):
            new_lines.append('DEVICE_NAME="Spotify Radio"\n')
        elif line.startswith("#USERNAME=") or line.startswith("USERNAME="):
            new_lines.append(f'USERNAME="{username}"\n')
        elif line.startswith("#PASSWORD=") or line.startswith("PASSWORD="):
            new_lines.append(f'PASSWORD="{password}"\n')
        else:
            new_lines.append(line)

    # Add username/password if not found
    if not any("USERNAME=" in l for l in new_lines):
        new_lines.append(f'USERNAME="{username}"\n')
    if not any("PASSWORD=" in l for l in new_lines):
        new_lines.append(f'PASSWORD="{password}"\n')

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

    if "spotify_username" in data and "spotify_password" in data:
        raspotify_set = configure_raspotify(data["spotify_username"], data["spotify_password"])

    if raspotify_set==True and wifi_set==True:
        return True
    else:
        return False

if __name__ == "__main__":
    time.sleep(5)  # Give time for USB to mount
    handle_config()