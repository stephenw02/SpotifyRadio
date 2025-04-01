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
    
def assign_role(role):
    """Updates Users table with user's active role (broadcaster/listener)"""
    response = supabase.table("Users").update({"active_role":role}).eq("pi_id", os.getenv("piID")).execute()
    if response.data:
        print(f"✅ Updated user role as: {role}")
    else:
        print("❌ Failed to update role:", response)

def remove_role():
    """Updates Users table with no active role"""
    response = supabase.table("Users").update({"active_role":""}).eq("pi_id", os.getenv("piID")).execute()
    if response.data:
        print(f"✅ Removed user role")
    else:
        print("❌ Failed to remove role:", response)

def get_broadcasters():
    """Gets count of Broadcasting Users from Supabase"""
    try:
        response = supabase.table("Users").select("id", count="exact").eq("active_role", "Broadcaster").execute()
        if response.status_code == 200:
            count = response.count
            #print(f"Number of broadcasters: {count}")
            return count
        else:
            print(f"Error fetching broadcasters: {response.status_code} - {response.error_message}")
            return 0
    except Exception as e:
        print(f"❌ Exception occurred while fetching broadcasters: {e}")
        return 0

def get_listeners():
    """Gets count of Listening Users from Supabase"""
    try:
        response = supabase.table("Users").select("id", count="exact").eq("active_role", "Listener").execute()
        if response.status_code == 200:
            count = response.count
            #print(f"Number of Listener: {count}")
            return count
        else:
            print(f"Error fetching listeners: {response.status_code} - {response.error_message}")
            return 0
    except Exception as e:
        print(f"❌ Exception occurred while fetching listeners: {e}")
        return 0