import requests
import time
import spotipy
from spotipy.oauth2 import SpotifyPKCE
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("supabaseURL")
SUPABASE_KEY = os.getenv("supabaseKey")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")  # Unused but required for Spotipy

# Raspberry Pi ID (match this with the one stored in Supabase)
PI_ID = os.getenv("piID")


def spotipy_readiness(access_token, refresh_token, expires_at):
    if access_token is None or refresh_token is None or expires_at is None:
        access_token, refresh_token, expires_at = fetch_tokens_from_supabase()

    if access_token is not None and refresh_token is not None and expires_at is not None:
        access_token, expires_at, refresh_token = ensure_valid_token(access_token, refresh_token, expires_at)
        sp = setup_spotipy(access_token)
        return sp, access_token, expires_at, refresh_token
    
    else:
        return None, None, None, None


def fetch_tokens_from_supabase():
    """Fetch the access and refresh tokens from Supabase using the Pi ID."""
    response = supabase.table("Tokens").select("*").eq("pi_id", PI_ID).execute()

    if response.data:
        record = response.data[0]
        access_token = record.get("access_token")
        refresh_token = record.get("refresh_token")
        expires_at = int(record.get("expires_at", 0))
        print("✅ Tokens fetched from Supabase.")
        return access_token, refresh_token, expires_at
    else:
        print("⚠️ No record found for this Pi ID in Supabase.")
        return None, None, None


def refresh_access_token(access_token, refresh_token, expires_at):
    """Use the refresh token to get a new access token and update Supabase."""
    if not refresh_token:
        print("❌ No refresh token available!")
        return

    auth_manager = SpotifyPKCE(
        client_id=SPOTIFY_CLIENT_ID,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope="user-read-playback-state user-modify-playback-state user-read-currently-playing"
    )

    try:
        token_info = auth_manager.refresh_access_token(refresh_token)
        access_token = token_info["access_token"]
        expires_at = token_info["expires_at"]
        refresh_token = token_info["refresh_token"]
        print("🔄 Access token refreshed!")
        # ✅ Update Supabase with the new access token and expiration time
        update_supabase_token(access_token, expires_at, refresh_token)
        return access_token, expires_at, refresh_token
    except Exception as e:
        print(f"Error refreshing token... {e}")
        return None, None, None


def update_supabase_token(new_access_token, new_expires_at, refresh_token):
    """Update the access token and expiration time in Supabase."""
    response = supabase.table("Tokens").update({
        "access_token": new_access_token,
        "expires_at": str(new_expires_at)
    }).eq("pi_id", PI_ID).execute()

    if response.data:
        print("✅ Supabase updated with new access token.")
        return new_access_token, new_expires_at, refresh_token
    else:
        print("❌ Error updating Supabase:", response.error)


def ensure_valid_token(access_token, refresh_token, expires_at):
    """Ensure that the access token is still valid; refresh if needed."""
    if time.time() > int(expires_at)-10:
        print("⚠️ Access token expired! Refreshing...")
        access_token, expires_at, refresh_token = refresh_access_token(access_token, refresh_token, expires_at)
    else:
        time_remaining = round((expires_at - time.time()) / 60, 2)
        # print("✅ Access token still valid! Time remaining: ", time_remaining, "mins")
    return access_token, expires_at, refresh_token


def setup_spotipy(access_token):
    """Initialize Spotipy with the current access token."""
    sp = spotipy.Spotify(auth=access_token)
    return sp