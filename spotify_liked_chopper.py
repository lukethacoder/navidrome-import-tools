import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

SCOPE = "user-library-read playlist-modify-private playlist-modify-public"

# Authenticate and create a Spotipy client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))

# Fetch all liked (saved) tracks
liked_tracks = []
limit = 50
offset = 0

print("Fetching liked songs...")
while True:
    results = sp.current_user_saved_tracks(limit=limit, offset=offset)
    items = results['items']
    if not items:
        break
    liked_tracks.extend([item['track']['id'] for item in items])
    offset += len(items)
    if offset % 100 == 0:
        print(f"Fetched {offset} liked songs so far...")

print(f"Fetched {len(liked_tracks)} liked songs.")

# Get current user id
user_id = sp.current_user()['id']

# Process liked tracks in batches of 500
batch_size = 500
for batch_num, start_idx in enumerate(range(0, len(liked_tracks), batch_size), start=1):
    # Create playlist name with batch number
    playlist_name = f"All My Liked Songs {batch_num}"
    
    # Create new playlist
    new_playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False)
    playlist_id = new_playlist['id']
    
    # Add tracks to the playlist in chunks of 100 (Spotify limit)
    batch_tracks = liked_tracks[start_idx:start_idx + batch_size]
    for i in range(0, len(batch_tracks), 100):
        sp.playlist_add_items(playlist_id, batch_tracks[i:i+100])
        print(f"Added tracks {start_idx + i + 1} to {start_idx + min(i+100, len(batch_tracks))} to playlist '{playlist_name}'.")

print("Added all liked songs into multiple playlists, each with up to 500 songs.")
