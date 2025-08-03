#!/usr/bin/env python3
import sqlite3
import json
import os

# Path to your Navidrome SQLite database file
DB_PATH = os.path.join(os.path.dirname(__file__), 'navidrome.db')

def navidrome_search_track_db(conn, track_name, artist_name):
    """Search Navidrome database for track by name and artist using SQL LIKE queries."""
    
    # Normalize artist names - handle different separators
    # Spotify uses "," but Navidrome uses "•"
    primary_artist = artist_name.split(',')[0].strip()  # Get first artist
    
    # Create multiple artist patterns to try
    artist_patterns = [
        f"%{artist_name.lower()}%",  # Original format
        f"%{primary_artist.lower()}%",  # Just primary artist
        f"%{artist_name.replace(',', ' •').lower()}%",  # Replace comma with bullet
        f"%{artist_name.replace(', ', ' • ').lower()}%",  # Replace comma+space with bullet
    ]
    
    # Create search patterns for fuzzy matching
    track_pattern = f"%{track_name.lower()}%"
    
    # Try exact title match first with multiple artist patterns
    for artist_pattern in artist_patterns:
        cursor = conn.execute("""
            SELECT id, path, title, artist, album, duration 
            FROM media_file 
            WHERE LOWER(title) = LOWER(?) 
            AND (LOWER(artist) LIKE ? OR LOWER(album_artist) LIKE ?)
            LIMIT 1
        """, (track_name, artist_pattern, artist_pattern))
        
        result = cursor.fetchone()
        if result:
            return {
                'id': result[0],
                'path': result[1], 
                'title': result[2],
                'artist': result[3],
                'album': result[4],
                'duration': result[5]
            }
    
    # Try partial title match (handles "feat." differences)
    core_track_name = track_name.split('(')[0].strip()  # Remove "(feat. ...)" parts
    core_pattern = f"%{core_track_name.lower()}%"
    
    for artist_pattern in artist_patterns:
        cursor = conn.execute("""
            SELECT id, path, title, artist, album, duration 
            FROM media_file 
            WHERE (LOWER(title) LIKE ? OR LOWER(title) LIKE ?)
            AND (LOWER(artist) LIKE ? OR LOWER(album_artist) LIKE ?)
            LIMIT 1
        """, (track_pattern, core_pattern, artist_pattern, artist_pattern))
        
        result = cursor.fetchone()
        if result:
            return {
                'id': result[0],
                'path': result[1],
                'title': result[2], 
                'artist': result[3],
                'album': result[4],
                'duration': result[5]
            }
    
    # Fallback: search by primary artist only in full text
    query_text = f"{track_name} {primary_artist}".lower()
    cursor = conn.execute("""
        SELECT id, path, title, artist, album, duration 
        FROM media_file 
        WHERE LOWER(full_text) LIKE ?
        LIMIT 1
    """, (f"%{query_text}%",))
    
    result = cursor.fetchone()
    if result:
        return {
            'id': result[0],
            'path': result[1],
            'title': result[2],
            'artist': result[3], 
            'album': result[4],
            'duration': result[5]
        }
    
    return None

def generate_m3u_from_db(spotify_playlist_json_path, output_path, test_mode=False):
    """Generate M3U playlist from Spotify JSON using direct database access."""
    
    with open(spotify_playlist_json_path, 'r', encoding='utf-8') as f:
        spotify_tracks = json.load(f)

    if test_mode:
        # Test with first 10 tracks only
        spotify_tracks = spotify_tracks[:10]
        print(f"Processing {len(spotify_tracks)} tracks (TEST MODE - first 10 only)...")
    else:
        print(f"Processing {len(spotify_tracks)} tracks...")
    
    lines = ['#EXTM3U', '#PLAYLIST:Spotify Imported Playlist']
    total_tracks = len(spotify_tracks)
    matched_count = 0
    processed_count = 0
    failed_matches = []

    # Simple progress indicator
    print(f"Processing tracks...", end="", flush=True)

    try:
        # Open database connection
        conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
        
        for i, track in enumerate(spotify_tracks):
            track_name = track['track_name']
            artist_name = track['artist_name']
            duration_sec = int(track['duration_ms'] / 1000)
            
            song = navidrome_search_track_db(conn, track_name, artist_name)
            if song:
                file_path = song['path']
                if file_path:
                    # Prepend /music/ to the file path
                    full_path = f"/music/{file_path}"
                    # Build EXTINF line
                    extinf = f"#EXTINF:{duration_sec},{artist_name} - {track_name}"
                    lines.append(extinf)
                    lines.append(full_path)
                    matched_count += 1
                else:
                    failed_matches.append({
                        'track_name': track_name,
                        'artist_name': artist_name,
                        'reason': 'No file path found'
                    })
            else:
                failed_matches.append({
                    'track_name': track_name,
                    'artist_name': artist_name,
                    'reason': 'No match found in database'
                })
            
            processed_count += 1
            
            # Simple progress indicator - print every few tracks
            if processed_count % 5 == 0 or processed_count == total_tracks:
                percent = int((processed_count / total_tracks) * 100)
                print(f"\r{percent}% ({processed_count}/{total_tracks}) - Matched: {matched_count}", end="", flush=True)

    except sqlite3.Error as e:
        print(f"\nSQLite error: {e}")
        return
    finally:
        if 'conn' in locals():
            conn.close()

    print(f"\nCompleted! Matched {matched_count} out of {total_tracks} tracks.")
    print(f"Success rate: {(matched_count/total_tracks)*100:.1f}%")

    # Write M3U file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"M3U playlist written to: {output_path}")
    
    # Write failed matches to JSON file for analysis
    if failed_matches:
        failed_file = output_path.replace('.m3u', '_failed_matches.json')
        with open(failed_file, 'w', encoding='utf-8') as f:
            json.dump(failed_matches, f, indent=2, ensure_ascii=False)
        print(f"Failed matches written to: {failed_file}")

def list_songs(conn, limit=5):
    """Fetch and print song info from the database."""
    cursor = conn.execute(f"SELECT id, path, title, artist, album, duration FROM media_file LIMIT {limit}")
    rows = cursor.fetchall()

    if not rows:
        print("No songs found in the database.")
        return

    print(f"Sample songs from database:\n")
    for row in rows:
        song = {
            'id': row[0],
            'path': row[1],
            'title': row[2],
            'artist': row[3],
            'album': row[4],
            'duration': row[5]
        }
        print(json.dumps(song, indent=2))
        print('-' * 40)

def main():
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'list':
            # List sample songs from database
            try:
                conn = sqlite3.connect(f'file:{DB_PATH}?mode=ro', uri=True)
                list_songs(conn)
            except sqlite3.Error as e:
                print(f"SQLite error: {e}")
            finally:
                if 'conn' in locals():
                    conn.close()
                    
        elif command == 'generate':
            # Generate M3U playlist
            spotify_json = sys.argv[2] if len(sys.argv) > 2 else 'playlist_tracks.json'
            output_file = sys.argv[3] if len(sys.argv) > 3 else 'navidrome_playlist.m3u'
            # test_mode = '--full' not in sys.argv
            
            if not os.path.exists(spotify_json):
                print(f"Error: Spotify playlist JSON file not found: {spotify_json}")
                return
                
            generate_m3u_from_db(spotify_json, output_file, test_mode=False)
        else:
            print("Unknown command. Use 'list' or 'generate'")
    else:
        print("Usage:")
        print("  python spoti_playlist_from_db.py list")
        print("  python spoti_playlist_from_db.py generate [spotify_json] [output_m3u] [--full]")
        print("\nExamples:")
        print("  python spoti_playlist_from_db.py generate playlist_tracks.json navidrome_playlist.m3u")
        print("  python spoti_playlist_from_db.py generate playlist_tracks.json navidrome_playlist.m3u --full")

if __name__ == '__main__':
    main()
