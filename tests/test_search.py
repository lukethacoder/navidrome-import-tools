#!/usr/bin/env python3
import requests
import json

NAVIDROME_URL = 'http://10.1.1.2:30043'
API_USER = 'ethan'
API_PASS = '^%QwtfggF6W2qDV'

def test_search_with_version():
    """Test search with proper version parameter"""
    
    # Test with a simple query first
    query = "test"
    url = f"{NAVIDROME_URL}/rest/search3.view"
    params = {
        'query': query,
        'u': API_USER,
        'p': API_PASS,
        'v': '1.16.1',  # Required version parameter
        'c': 'spotify_playlist_converter',  # Required client parameter
        'f': 'json'     # Explicitly request JSON format
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response text: {response.text[:1000]}")
        
        if response.text:
            data = response.json()
            print(f"JSON structure: {json.dumps(data, indent=2)}")
            
            # Check the structure
            if 'subsonic-response' in data:
                if data['subsonic-response'].get('status') == 'ok':
                    search_result = data['subsonic-response'].get('searchResult3', {})
                    songs = search_result.get('song', [])
                    print(f"Found {len(songs)} songs")
                    if songs:
                        print(f"First song: {songs[0]}")
                else:
                    error = data['subsonic-response'].get('error', {})
                    print(f"API Error: {error}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_search_with_version()
