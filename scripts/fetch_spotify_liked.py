import spotipy
from spotipy.oauth2 import SpotifyOAuth
import csv
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPE = "user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))

liked_tracks = []
limit = 50
offset = 0

print("Fetching user's liked songs...")
while True:
    results = sp.current_user_saved_tracks(limit=limit, offset=offset)
    items = results['items']
    if not items:
        break
    for item in items:
        track = item['track']
        if track is None:  # skip removed tracks
            continue
        liked_tracks.append({
            'track_id': track['id'],
            'track_name': track['name'],
            'artist_name': ', '.join([artist['name'] for artist in track['artists']]),
            'artist_id': ', '.join([artist['id'] for artist in track['artists']]),
            'album_name': track['album']['name'],
            'album_id': track['album']['id'],
            'added_at': item.get('added_at', ''),
            'track_uri': track['uri'],
            'popularity': track.get('popularity', ''),
            'duration_ms': track.get('duration_ms', '')
        })
    offset += len(items)
    print(f"Fetched {offset} liked songs so far...")

print(f"Fetched a total of {len(liked_tracks)} liked songs.")

# Save to JSON
with open('liked_tracks.json', 'w', encoding='utf-8') as f:
    json.dump(liked_tracks, f, ensure_ascii=False, indent=2)
print("Exported liked songs to liked_tracks.json")

# Save to CSV (optional)
if liked_tracks:
    keys = liked_tracks[0].keys()
    with open('liked_tracks.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(liked_tracks)
    print("Exported liked songs to liked_tracks.csv")
else:
    print("No tracks found to export.")
