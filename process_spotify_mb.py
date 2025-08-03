import csv
import json
import re
import requests
import time
import unicodedata

# Config: Set your input/output files and max albums to query
INPUT_FILE = 'playlist_tracks.json'  # or 'playlist_tracks.csv'
IS_JSON = INPUT_FILE.endswith('.json')
OUTPUT_FILE = 'lidarr_mb_releasegroups.json'
FAILED_MATCHES_FILE = 'failed_matches.json'
MAX_ALBUMS = 1000000  # Limit output to first 10 unique albums for testing

# Function to clean and normalize strings for querying MusicBrainz
def clean_string(s):
    if not s:
        return ''
    # Normalize unicode, remove diacritics
    s = ''.join([c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c)])
    # Remove non-printable/control characters
    s = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', str(s))
    # Replace curly apostrophes and quotes with ascii equivalents (optional)
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    # Strip leading/trailing whitespace
    s = s.strip()
    return s

# Read the playlist export file (JSON or CSV)
playlist_tracks = []
if IS_JSON:
    with open(INPUT_FILE, encoding='utf-8') as f:
        playlist_tracks = json.load(f)
else:
    with open(INPUT_FILE, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            playlist_tracks.append(row)

# Extract unique albums keyed by normalized (artist, album) using only first artist
albums = {}
track_to_album_map = {}  # Map each track to its album key for failed match tracking

for entry in playlist_tracks:
    artist_raw = entry.get('artist_name') or entry.get('artist') or ''
    album_raw = entry.get('album_name') or entry.get('album') or ''
    if not album_raw or not artist_raw:
        continue

    # Use only the first artist before a comma
    primary_artist = clean_string(artist_raw.split(',')[0])
    album = clean_string(album_raw)

    key = (primary_artist.lower(), album.lower())
    if key not in albums:
        albums[key] = {
            'artist': primary_artist, 
            'album': album,
            'tracks': []  # Store associated tracks for failed match reporting
        }
    
    # Add this track to the album's track list
    albums[key]['tracks'].append(entry)
    track_to_album_map[id(entry)] = key

# Function to query MusicBrainz release-group by artist and album title
def query_mb_releasegroup(artist, album):
    base_url = 'https://musicbrainz.org/ws/2/release-group/'
    headers = {
        'User-Agent': 'LidarrMBImportScript/1.0 (youremail@example.com)'
    }

    query_parts = []
    if album:
        query_parts.append(f'releasegroup:"{album}"')
    if artist:
        query_parts.append(f'artist:"{artist}"')
    query = ' AND '.join(query_parts)
    if not query:
        return None

    params = {
        'query': query,
        'fmt': 'json',
        'limit': 1
    }

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        if 'release-groups' in data and len(data['release-groups']) > 0:
            return data['release-groups'][0]['id']
    except Exception as e:
        print(f"Error querying MusicBrainz for artist='{artist}', album='{album}': {e}")
    return None

# Query MusicBrainz for each unique album (up to MAX_ALBUMS)
result = []
failed_matches = []
count = 0

print(f"Found {len(albums)} unique albums. Querying MusicBrainz for up to {MAX_ALBUMS} albums...")

for (artist_key, album_key), info in albums.items():
    # if count >= MAX_ALBUMS:
    #     break
    artist = info['artist']
    album = info['album']
    tracks = info['tracks']
    print(f"Querying for Artist: '{artist}' | Album: '{album}'")

    mb_id = query_mb_releasegroup(artist, album)

    # Fallback: if no result and artist was used, try album only
    if not mb_id and artist:
        print(f"  Fallback: retrying with album only (no artist)")
        mb_id = query_mb_releasegroup('', album)

    if mb_id:
        print(f"  Found MusicBrainz Release Group ID: {mb_id}")
        result.append({"MusicBrainzId": mb_id})
    else:
        print(f"  Could not find MusicBrainz ID for Album '{album}' by '{artist}'")
        # Add failed match info with associated tracks
        failed_match = {
            "artist": artist,
            "album": album,
            "tracks": tracks
        }
        failed_matches.append(failed_match)

    count += 1
    # Respect MusicBrainz API rate limit — max 1 request per second
    time.sleep(1.1)

# Write the results to JSON file formatted for Lidarr
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

# Write the failed matches to a separate JSON file
with open(FAILED_MATCHES_FILE, 'w', encoding='utf-8') as f:
    json.dump(failed_matches, f, indent=2, ensure_ascii=False)

print(f"Exported {len(result)} MusicBrainz Release Group IDs to '{OUTPUT_FILE}'")
print(f"Exported {len(failed_matches)} failed matches to '{FAILED_MATCHES_FILE}'")
