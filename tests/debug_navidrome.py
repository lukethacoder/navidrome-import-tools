#!/usr/bin/env python3
import requests
import json

NAVIDROME_URL = 'http://10.1.1.2:30043'
API_USER = 'ethan'
API_PASS = '^%QwtfggF6W2qDV'

def test_navidrome_api():
    """Test basic connectivity to Navidrome API"""
    
    # Test 1: Basic ping/status
    print("Testing Navidrome connectivity...")
    try:
        ping_url = f"{NAVIDROME_URL}/rest/ping.view"
        ping_params = {
            'u': API_USER,
            'p': API_PASS,
            'f': 'json'
        }
        print(f"Ping URL: {ping_url}")
        print(f"Ping params: {ping_params}")
        
        response = requests.get(ping_url, params=ping_params, timeout=5)
        print(f"Ping response status: {response.status_code}")
        print(f"Ping response headers: {dict(response.headers)}")
        print(f"Ping response text: {response.text[:500]}")
        
        if response.text:
            try:
                ping_data = response.json()
                print(f"Ping JSON: {ping_data}")
            except json.JSONDecodeError as e:
                print(f"Ping JSON decode error: {e}")
        
    except Exception as e:
        print(f"Ping error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Simple search
    print("Testing search API...")
    try:
        search_url = f"{NAVIDROME_URL}/rest/search3.view"
        search_params = {
            'query': 'test',
            'u': API_USER,
            'p': API_PASS,
            'f': 'json'
        }
        print(f"Search URL: {search_url}")
        print(f"Search params: {search_params}")
        
        response = requests.get(search_url, params=search_params, timeout=5)
        print(f"Search response status: {response.status_code}")
        print(f"Search response headers: {dict(response.headers)}")
        print(f"Search response text: {response.text[:500]}")
        
        if response.text:
            try:
                search_data = response.json()
                print(f"Search JSON: {search_data}")
            except json.JSONDecodeError as e:
                print(f"Search JSON decode error: {e}")
        
    except Exception as e:
        print(f"Search error: {e}")

if __name__ == '__main__':
    test_navidrome_api()
