import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Supabase Config
SUPABASE_URL = os.getenv("supabaseURL")
SUPABASE_KEY = os.getenv("supabaseKey")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def update_track(track_data):
    """Replace the track in the Supabase Playing table (ensures only one track is stored)."""
    # First, delete the existing entry
    supabase.table("Playing").delete().neq("track_uri", "").execute()  # Deletes all entries

    # Then, insert the new one
    response = supabase.table("Playing").insert(track_data).execute()

    if response.data:
        print(f"✅ Updated Supabase with: {track_data['song']} by {track_data['artist']}")
    else:
        print("❌ Failed to update Supabase:", response)

def get_latest_track():
    """Fetch the most recent track from Supabase."""
    response = supabase.table("Playing").select("*").limit(1).execute()

    if response.data:
        latest_track = response.data[0]  # Get the most recent track
        return latest_track
    else:
        print("⚠️ No track data found in Supabase.")
        return {"error": "No track data found"}