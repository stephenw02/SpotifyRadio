import requests
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyPKCE
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Airtable credentials
AIRTABLE_URL = os.getenv("airtableURL")
AIRTABLE_API_KEY = os.getenv("airtableToken")

# Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI") # Unused but required for Spotipy

# Raspberry Pi ID (match this with the one stored in Airtable)
PI_ID = os.getenv("piID")

def spotipy_readiness(access_token, refresh_token, expires_at):
    if access_token == None or refresh_token == None or expires_at == None:
        access_token, refresh_token, expires_at = fetch_tokens_from_airtable()
    access_token, expires_at, refresh_token = ensure_valid_token(access_token, refresh_token, expires_at)

    sp = setup_spotipy(access_token)
    return sp, access_token, expires_at, refresh_token

def fetch_tokens_from_airtable():
    """Fetch the access and refresh tokens from Airtable using the Pi ID."""
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
    url = f"{AIRTABLE_URL}?filterByFormula={{piID}}='{PI_ID}'"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        records = response.json().get("records", [])
        if records:
            record = records[0]["fields"]
            access_token = record.get("access_token")
            refresh_token = record.get("refresh_token")
            expires_at = int(record.get("expires_at", 0))
            print("✅ Tokens fetched from Airtable.")
            return access_token, refresh_token, expires_at
        else:
            print("⚠️ No record found for this Pi ID in Airtable.")
    else:
        print("❌ Error fetching tokens from Airtable:", response.text)

def refresh_access_token(access_token, refresh_token, expires_at):
    """Use the refresh token to get a new access token and update Airtable."""

    if not refresh_token:
        print("❌ No refresh token available!")
        return

    auth_manager = SpotifyPKCE(
        client_id=SPOTIFY_CLIENT_ID,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope="user-read-playback-state user-modify-playback-state user-read-currently-playing"
    )

    token_info = auth_manager.get_cached_token()
    access_token = token_info["access_token"]
    expires_at = token_info["expires_at"]

    print("🔄 Access token refreshed!")

    # ✅ Update Airtable with the new access token and expiration time
    update_airtable_token(access_token, expires_at, refresh_token)

    return access_token, expires_at, refresh_token
    
def update_airtable_token(new_access_token, new_expires_at, refresh_token):
    """Update the access token and expiration time in Airtable."""
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Find the correct record to update
    url = f"{AIRTABLE_URL}?filterByFormula={{piID}}='{PI_ID}'"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        records = response.json().get("records", [])
        if records:
            record_id = records[0]["id"]
            update_url = f"{AIRTABLE_URL}/{record_id}"
            data = {
                "fields": {
                    "access_token": new_access_token,
                    "expires_at": str(new_expires_at)
                }
            }
            update_response = requests.patch(update_url, headers=headers, json=data)

            if update_response.status_code == 200:
                print("✅ Airtable updated with new access token.")
                return new_access_token, new_expires_at, refresh_token
            else:
                print("❌ Error updating Airtable:", update_response.text)
        else:
            print("⚠️ No record found for this Pi ID in Airtable.")
    else:
        print("❌ Error fetching record from Airtable:", response.text)

def ensure_valid_token(access_token, refresh_token, expires_at):
    """Ensure that the access token is still valid; refresh if needed."""
    if time.time() > int(expires_at):
        print("⚠️ Access token expired! Refreshing...")
        access_token, expires_at, refresh_token = refresh_access_token(access_token, refresh_token, expires_at)
    else:
        time_remaining = round((expires_at - time.time())/60,2)
        #print("✅ Access token still valid! Time remaining: ", time_remaining, " mins")
    return access_token, expires_at, refresh_token

def setup_spotipy(access_token):
    """Initialize Spotipy with the current access token."""
    sp = spotipy.Spotify(auth=access_token)
    return sp