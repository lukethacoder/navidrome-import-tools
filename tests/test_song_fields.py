#!/usr/bin/env python3
import requests
import json

NAVIDROME_URL = 'http://10.1.1.2:30043'
API_USER = 'ethan'
API_PASS = '^%QwtfggF6W2qDV'

def test_song_fields():
    """Test what fields are available in a song response"""
    
    query = "Ma, I Don't Love Her Faith Evans"
    url = f"{NAVIDROME_URL}/rest/search3.view"
    params = {
        'query': query,
        'u': API_USER,
        'p': API_PASS,
        'v': '1.16.1',
        'c': 'test',
        'f': 'json'
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        
        if 'subsonic-response' in data and data['subsonic-response'].get('status') == 'ok':
            search_result = data['subsonic-response'].get('searchResult3', {})
            songs = search_result.get('song', [])
            
            if songs:
                print("Available fields in song object:")
                print(json.dumps(songs[0], indent=2))
            else:
                print("No songs found")
        else:
            print("API error:", data)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_song_fields()
