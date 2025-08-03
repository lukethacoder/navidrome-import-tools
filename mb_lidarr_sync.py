import json
import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ====== CONFIGURATION ======
LIDARR_URL = os.getenv('LIDARR_URL')  # Your Lidarr API base URL
API_KEY = os.getenv('API_KEY')  # Your Lidarr API Key here
RELEASEGROUPS_FILE = "lidarr_mb_releasegroups.json"
ROOT_FOLDER_PATH = "/music/"  # Must match your Lidarr configured root folder
METADATA_PROFILE_ID = 1       # Adjust to your metadata profile ID in Lidarr
QUALITY_PROFILE_ID = 1        # Adjust to your quality profile ID in Lidarr
REQUEST_DELAY = 1.1           # Seconds between API requests

HEADERS = {"X-Api-Key": API_KEY}


def safe_get_first(data):
    if isinstance(data, list):
        return data[0] if data else None
    return data


def get_album_by_releasegroup(mb_release_group_id):
    term_value = "lidarr:" + str(mb_release_group_id)
    params = {"term": term_value}
    try:
        r = requests.get(f"{LIDARR_URL}/album/lookup", headers=HEADERS, params=params)
        if r.status_code == 200:
            data = r.json()
            return data if data else None
        # print(f"Album lookup failed for MBID {mb_release_group_id} with status {r.status_code}")
    except Exception as e:
        # print(f"Exception during album lookup for MBID {mb_release_group_id}: {e}")
        pass
    return None


def get_artist_by_mb_id(artist_mb_id):
    term_value = "lidarr:" + str(artist_mb_id)
    params = {"term": term_value}
    try:
        r = requests.get(f"{LIDARR_URL}/artist/lookup", headers=HEADERS, params=params)
        if r.status_code == 200:
            data = r.json()
            return data if data else None
        # print(f"Artist lookup failed for MBID {artist_mb_id} with status {r.status_code}")
    except Exception as e:
        # print(f"Exception during artist lookup for MBID {artist_mb_id}: {e}")
        pass
    return None


def add_artist(artist_mb_id):
    resp = get_artist_by_mb_id(artist_mb_id)
    if resp:
        artist_data = safe_get_first(resp)
        if artist_data and artist_data.get("id"):
            return artist_data["id"]
        else:
            try:
                lookup = requests.get(f"{LIDARR_URL}/artist/lookup", headers=HEADERS,
                                      params={'term': "lidarr:" + str(artist_mb_id)})
                if lookup.status_code == 200:
                    artist_data = safe_get_first(lookup.json())
                    if artist_data:
                        artist_data['metadataProfileId'] = METADATA_PROFILE_ID
                        artist_data['qualityProfileId'] = QUALITY_PROFILE_ID
                        artist_data['rootFolderPath'] = ROOT_FOLDER_PATH

                        add = requests.post(f"{LIDARR_URL}/artist", headers=HEADERS, json=artist_data)
                        if add.status_code in (200, 201):
                            artist_id = add.json().get("id")
                            print(f"  ✓ Added artist: {artist_data.get('artistName', artist_mb_id)}")
                            time.sleep(2)  # Wait for Lidarr to register artist fully
                            return artist_id
                        else:
                            print(f"  ✗ Failed to add artist {artist_mb_id}")
                    else:
                        print(f"  ✗ No artist data found for {artist_mb_id}")
                else:
                    print(f"  ✗ Artist lookup failed for {artist_mb_id}")
            except Exception as e:
                print(f"  ✗ Exception adding artist {artist_mb_id}")
    else:
        print(f"  ✗ No artist lookup response for {artist_mb_id}")
    return None


def monitor_album_if_needed(album):
    album_id = album.get("id")
    if album_id is None:
        return False

    if album.get("monitored", False):
        return True

    album["monitored"] = True
    try:
        resp = requests.put(f"{LIDARR_URL}/album/{album_id}", headers=HEADERS, json=album)
        if resp.status_code in (200, 202):
            return True
        else:
            return False
    except Exception as e:
        return False


def trigger_album_search(album_id, album_title):
    if album_id is None:
        return
    command_json = {"name": "AlbumSearch", "albumIds": [album_id]}
    try:
        resp = requests.post(f"{LIDARR_URL}/command", headers=HEADERS, json=command_json)
        if resp.status_code in (200, 201):
            print(f"  → Search triggered for '{album_title}'")
        else:
            print(f"  ✗ Search failed for '{album_title}'")
    except Exception as e:
        print(f"  ✗ Search exception for '{album_title}'")


def extract_artist_mb_id(album_info):
    artist_mb_id = None
    artist = album_info.get("artist")
    if artist:
        artist_mb_id = artist.get("foreignArtistId") or artist.get("musicBrainzId")
    if not artist_mb_id:
        artist_id_val = album_info.get("artistId")
        if artist_id_val and isinstance(artist_id_val, str) and artist_id_val != "0":
            artist_mb_id = artist_id_val
    return artist_mb_id


def first_pass_add_artists(groups):
    """Add all unique artists from albums upfront. Return mapping of MBID to Lidarr artist ID."""
    artist_map = {}
    processed_artist_mbids = set()

    print(f"🎵 PASS 1: Adding artists")
    for i, entry in enumerate(groups):
        mb_id = entry.get("MusicBrainzId")
        if not mb_id:
            continue
        
        print(f"  Processing artist {i + 1}/{len(groups)}: {mb_id}")
        album_info = get_album_by_releasegroup(mb_id)
        album_info = safe_get_first(album_info)
        if not album_info:
            print(f"  ✗ Lookup failed for album {mb_id}")
            continue
        
        artist_mb_id = extract_artist_mb_id(album_info)
        if not artist_mb_id:
            print(f"  ✗ No artist MBID found for album {mb_id}")
            continue
            
        if artist_mb_id in processed_artist_mbids:
            print(f"  ⚬ Artist already processed: {artist_mb_id}")
            continue
            
        artist_id = add_artist(artist_mb_id)
        if artist_id:
            artist_map[artist_mb_id] = artist_id
        processed_artist_mbids.add(artist_mb_id)
        
    print(f"✅ PASS 1 Complete: {len(artist_map)} artists added/found")
    return artist_map


def second_pass_add_albums(groups, artist_map):
    print(f"💿 PASS 2: Adding albums")
    success_count = 0
    fail_count = 0
    existing_count = 0
    
    for i, entry in enumerate(groups):
        mb_id = entry.get("MusicBrainzId")
        if not mb_id:
            continue
            
        print(f"Processing album {i + 1}/{len(groups)}: {mb_id}")
        album_info = get_album_by_releasegroup(mb_id)
        album_info = safe_get_first(album_info)
        if not album_info:
            print(f"  ✗ Lookup failed for album {mb_id}")
            fail_count += 1
            continue
            
        artist_mb_id = extract_artist_mb_id(album_info)
        if not artist_mb_id or artist_mb_id not in artist_map:
            print(f"  ✗ Artist MBID missing in artist map for album {mb_id}")
            fail_count += 1
            continue
            
        artist_id = artist_map[artist_mb_id]

        # Check if album already exists
        if album_info.get("id"):
            print(f"  ⚬ Already exists: {album_info.get('title')}")
            existing_count += 1
            # Ensure monitored and trigger search
            monitored = monitor_album_if_needed(album_info)
            if monitored:
                trigger_album_search(album_info.get("id"), album_info.get("title"))
            continue

        # Prepare album info to add
        album_body = album_info
        album_body['artistId'] = artist_id
        album_body['metadataProfileId'] = METADATA_PROFILE_ID
        album_body['qualityProfileId'] = QUALITY_PROFILE_ID
        album_body['monitored'] = True
        album_body['addOptions'] = {"searchForMissingAlbums": True}

        try:
            add_resp = requests.post(f"{LIDARR_URL}/album", headers=HEADERS, json=album_body)
            if add_resp.status_code in (200, 201):
                album_id = add_resp.json().get("id")
                print(f"  ✓ Added: {album_info.get('title')}")
                success_count += 1
                trigger_album_search(album_id, album_info.get('title'))
            else:
                print(f"  ✗ Add failed for {mb_id}")
                fail_count += 1
        except Exception as e:
            print(f"  ✗ Exception adding album {mb_id}")
            fail_count += 1
        time.sleep(REQUEST_DELAY)
    
    print(f"✅ PASS 2 Complete: {success_count} added, {existing_count} existing, {fail_count} failed")


def main():
    try:
        with open(RELEASEGROUPS_FILE, encoding="utf-8") as f:
            groups = json.load(f)
    except Exception as e:
        print(f"Failed to load {RELEASEGROUPS_FILE}: {e}")
        return

    print(f"📚 Loaded {len(groups)} MusicBrainz Release Group IDs.")
    
    test_groups = groups
    print(f"🧪 Testing with first {len(test_groups)} albums")
    
    artist_map = first_pass_add_artists(test_groups)
    second_pass_add_albums(test_groups, artist_map)


if __name__ == "__main__":
    main()
