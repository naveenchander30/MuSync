import os
import requests
import json
import webbrowser
import time
from rapidfuzz.fuzz import ratio, partial_ratio, token_sort_ratio

def find_best_spotify_track_uri(track_name, track_artists, headers):
    url = "https://api.spotify.com/v1/search"
    params = {
        'q': f"{track_name}",
        'type': 'track',
        'limit': 3
    }
    search_response = requests.get(url, headers=headers, params=params)
    if search_response.status_code == 200:
        search_data = search_response.json()
        tracks_data = search_data.get('tracks', {}).get('items', [])
        track_name = track_name.lower()
        track_artists = [artist.lower() for artist in track_artists]
        best_score = 0
        best_uri = None
        for item in tracks_data:
            item_name = item.get('name', '').lower()
            name_score = token_sort_ratio(item_name, track_name) * 1.5
            item_artists = [artist.get('name', '').lower() for artist in item.get('artists', [])]
            artist_score = sum(partial_ratio(a, ta) > 80 for a in item_artists for ta in track_artists) * 10
            total_score = name_score + artist_score
            if total_score > best_score:
                best_score = total_score
                best_uri = item.get('uri')
        return best_uri
    return None

print("Starting Spotify import...")
webbrowser.open(f"https://musync-k60r.onrender.com/spotify/login")

def wait_for_callback():
    print("Waiting for Spotify callback...")
    input("Press Enter after the callback is received...")

wait_for_callback()
print("Getting authentication tokens...")
response = requests.get('https://musync-k60r.onrender.com/spotify/tokens')
if response.status_code == 200:
    tokens = response.json()
    ACCESS_TOKEN = tokens.get('access_token')
    print("Authentication successful!")
else:
    print(f"Error getting authentication tokens: {response.status_code}")
    exit(1)
    
SPOTIFY_HEADER = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
}

print("Getting user information...")
url = "https://api.spotify.com/v1/me"
user_info = requests.get(url, headers=SPOTIFY_HEADER)
if user_info.status_code == 200:
    USER_ID = user_info.json().get('id')
    print(f"User ID: {USER_ID}")
else:
    print(f"Error getting user info: {user_info.status_code}")
    exit(1)

start_time = time.time()
print("Loading playlists from file...")
with open('playlists.json', 'r', encoding='utf-8') as f:
    all_playlists = json.load(f)

print("Getting existing playlists...")
url = f"https://api.spotify.com/v1/me/playlists?limit=50"
existing_playlist_names = {}
while url:
    existing_playlists = requests.get(url, headers=SPOTIFY_HEADER)
    if existing_playlists.status_code == 200:
        existing_playlists_data = existing_playlists.json().get('items', [])
        existing_playlist_names.update({playlist.get('name'): playlist.get('id') for playlist in existing_playlists_data})
        next_url = existing_playlists.json().get('next')
        url = next_url if next_url else None
print(f"Found {len(existing_playlist_names)} existing playlists")

skipped_tracks = 0
not_found_tracks = 0
added_tracks = 0
total_tracks = sum(len(playlist.get('tracks', [])) for playlist in all_playlists)

for i, playlist in enumerate(all_playlists, 1):
    playlist_name = playlist.get('name')
    tracks = playlist.get('tracks', [])
    print(f"\nProcessing playlist ({i}/{len(all_playlists)}): {playlist_name} - {len(tracks)} tracks")
    
    if playlist_name in existing_playlist_names:
        print(f"Playlist already exists, adding tracks to existing playlist")
        url = f"https://api.spotify.com/v1/playlists/{existing_playlist_names[playlist_name]}/tracks?limit=50"
        existing_track_uris = []
        while url:
            existing_tracks = requests.get(url, headers=SPOTIFY_HEADER)
            if existing_tracks.status_code == 200:
                existing_tracks_data = existing_tracks.json().get('items', [])
                existing_track_uris.extend([item.get('track', {}).get('uri') for item in existing_tracks_data if item.get('track')])
                next_url = existing_tracks.json().get('next')
                url = next_url if next_url else None
                
        print(f"Found {len(existing_track_uris)} existing tracks in playlist")
        for track in tracks:
            track_name = track.get('name')
            track_artists = track.get('artists', [])
            artists_str = ", ".join(track_artists) if track_artists else "Unknown"
            
            track_uri = find_best_spotify_track_uri(track_name, track_artists, SPOTIFY_HEADER)
            if not track_uri:
                print(f"  NOT FOUND: \"{track_name}\" by {artists_str}")
                not_found_tracks += 1
                continue
                
            if track_uri in existing_track_uris:
                skipped_tracks += 1
                continue
                
            add_url = f"https://api.spotify.com/v1/playlists/{existing_playlist_names[playlist_name]}/tracks"
            data = {
                'uris': [track_uri]
            }
            add_response = requests.post(add_url, headers=SPOTIFY_HEADER, json=data)
            if add_response.status_code in (201, 200):
                added_tracks += 1
            else:
                print(f"  ERROR ADDING: \"{track_name}\" by {artists_str} - {add_response.status_code}")
    else:
        print(f"Creating new playlist: {playlist_name}")
        url = f"https://api.spotify.com/v1/users/{USER_ID}/playlists"
        data = {
            'name': playlist_name,
            'public': True
        }
        response = requests.post(url, headers=SPOTIFY_HEADER, json=data)
        if response.status_code == 201:
            playlist_id = response.json().get('id')
            for track in tracks:
                track_name = track.get('name')
                track_artists = track.get('artists', [])
                artists_str = ", ".join(track_artists) if track_artists else "Unknown"
                
                track_uri = find_best_spotify_track_uri(track_name, track_artists, SPOTIFY_HEADER)
                if not track_uri:
                    print(f"  NOT FOUND: \"{track_name}\" by {artists_str}")
                    not_found_tracks += 1
                    continue
                    
                add_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
                data = {
                    'uris': [track_uri]
                }
                add_response = requests.post(add_url, headers=SPOTIFY_HEADER, json=data)
                if add_response.status_code in (201, 200):
                    added_tracks += 1
                else:
                    print(f"  ERROR ADDING: \"{track_name}\" by {artists_str} - {add_response.status_code}")
        else:
            print(f"Error creating playlist: {response.status_code}")

print("\nProcessing liked songs...")
with open('liked.json', 'r', encoding='utf-8') as f:
    liked_tracks = json.load(f)
    
print(f"Found {len(liked_tracks)} liked songs")
url = f"https://api.spotify.com/v1/me/tracks?limit=50"
existing_liked_tracks_url = []
while url:
    existing_liked_tracks = requests.get(url, headers=SPOTIFY_HEADER)
    if existing_liked_tracks.status_code == 200:
        existing_liked_tracks_data = existing_liked_tracks.json().get('items', [])
        existing_liked_tracks_url.extend([item.get('track', {}).get('uri') for item in existing_liked_tracks_data if item.get('track')])
        next_url = existing_liked_tracks.json().get('next')
        url = next_url if next_url else None
        
print(f"Found {len(existing_liked_tracks_url)} existing liked tracks")
liked_added = 0
liked_skipped = 0
liked_not_found = 0

for track in liked_tracks:
    track_name = track.get('name')
    track_artists = track.get('artists', [])
    artists_str = ", ".join(track_artists) if track_artists else "Unknown"
    
    track_uri = find_best_spotify_track_uri(track_name, track_artists, SPOTIFY_HEADER)
    if not track_uri:
        print(f"  NOT FOUND: \"{track_name}\" by {artists_str}")
        liked_not_found += 1
        continue
        
    if track_uri in existing_liked_tracks_url:
        liked_skipped += 1
        continue
        
    add_url = "https://api.spotify.com/v1/me/tracks"
    data = {
        'ids': [track_uri.split(':')[-1]]  # Extract the track ID from the URI
    }
    add_response = requests.put(add_url, headers=SPOTIFY_HEADER, json=data)
    if add_response.status_code in (200, 201):
        liked_added += 1
    else:
        print(f"  ERROR ADDING LIKE: \"{track_name}\" by {artists_str} - {add_response.status_code}")

# Print summary statistics
end_time = time.time()
execution_time = end_time - start_time
print("\nImport Summary:")
print(f"Playlists processed: {len(all_playlists)}")
print(f"Playlist tracks: {added_tracks} added, {skipped_tracks} skipped, {not_found_tracks} not found")
print(f"Liked tracks: {liked_added} added, {liked_skipped} skipped, {liked_not_found} not found")
print(f"Total time: {execution_time:.2f} seconds")
