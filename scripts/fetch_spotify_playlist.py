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
SCOPE = "playlist-read-private playlist-read-collaborative"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))

# Put your playlist ID here (the part after 'playlist/' in the URL)
PLAYLIST_ID = '3cXFWPgBhhMy3k2z8HXama'

playlist_tracks = []
limit = 100
offset = 0

print("Fetching playlist tracks...")
while True:
    results = sp.playlist_items(PLAYLIST_ID, limit=limit, offset=offset)
    items = results['items']
    if not items:
        break
    for item in items:
        track = item['track']
        if track is None:  # skip removed tracks
            continue
        playlist_tracks.append({
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
    if offset % 200 == 0:
        print(f"Fetched {offset} playlist songs so far...")

print(f"Fetched {len(playlist_tracks)} playlist songs.")

# Save to JSON
with open('playlist_tracks.json', 'w', encoding='utf-8') as f:
    json.dump(playlist_tracks, f, ensure_ascii=False, indent=2)
print("Exported playlist songs to playlist_tracks.json")

# Save to CSV
if playlist_tracks:
    keys = playlist_tracks[0].keys()
    with open('playlist_tracks.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, keys)
        writer.writeheader()
        writer.writerows(playlist_tracks)
    print("Exported playlist songs to playlist_tracks.csv")
else:
    print("No tracks found to export.")
