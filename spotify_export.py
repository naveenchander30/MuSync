import os
import requests
import json
import webbrowser
import time

print("Starting Spotify export...")
webbrowser.open(f"https://musync-k60r.onrender.com/spotify/login")

def wait_for_callback():
    print("Waiting for Spotify callback...")
    input("Press Enter after the callback is received...")
    
wait_for_callback()

print("Getting authentication tokens...")
response= requests.get('https://musync-k60r.onrender.com/spotify/tokens')
if response.status_code == 200:
    tokens = response.json()
    ACCESS_TOKEN = tokens.get('access_token')
    print("Authentication successful!")
else:
    print(f"Error getting authentication tokens: {response.status_code}")
    exit(1)
    
SPOTIFY_HEADER={
    "Authorization": f"Bearer {ACCESS_TOKEN}",
}

url="https://api.spotify.com/v1/me"
user_info=requests.get(url,headers=SPOTIFY_HEADER)
if user_info.status_code == 200:
    USER_ID= user_info.json().get('id')
else:
    print(f"Error getting user info: {user_info.status_code}")
    exit(1)

start_time = time.time()
all_playlists = []
url=f"https://api.spotify.com/v1/me/playlists?limit=50"
print("Fetching playlists...")

while url:
    playlists=requests.get(url, headers=SPOTIFY_HEADER)
    if playlists.status_code == 200:
        playlists_data = playlists.json().get('items', [])
        print(f"Found {len(playlists_data)} playlists in this batch")
        
        for playlist in playlists_data:
            playlist_name = playlist.get('name')
            if not playlist_name:
                continue
                
            print(f"Processing playlist: {playlist_name}")
            playlist_info = {
                'name': playlist_name,
                'tracks': [],
            }

            tracks_url = playlist.get('tracks', {}).get('href')
            if tracks_url:
                while tracks_url:
                    tracks = requests.get(tracks_url, headers=SPOTIFY_HEADER)
                    if tracks.status_code == 200:
                        tracks_data = tracks.json()
                        for track in tracks_data.get('items', []):
                            track_obj = track.get('track', {})
                            if not track_obj:
                                continue
                            track_type = track_obj.get('type')
                            track_name = track_obj.get('name')
                            
                            if not track_name:
                                continue
                                
                            if track_type == 'track':
                                track_artists = [artist.get('name') for artist in track_obj.get('artists', []) if artist.get('name')]
                                playlist_info['tracks'].append({
                                    'name': track_name,
                                    'artists': track_artists,
                                })
                        
                        tracks_url = tracks_data.get('next')
                    else:
                        print(f"Error fetching tracks: {tracks.status_code}")
                        tracks_url = None
            
            all_playlists.append(playlist_info)
        
        url = playlists.json().get('next')
    else:
        print(f"Error fetching playlists: {playlists.status_code}")
        url = None
with open('playlists.json', 'w',encoding='utf-8') as f:
    json.dump(all_playlists, f, ensure_ascii=False,indent=4)

print("\nFetching liked songs...")
url=f"https://api.spotify.com/v1/me/tracks?limit=50"
liked_tracks = []
while url:
    response = requests.get(url, headers=SPOTIFY_HEADER)
    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])
        for item in items:
            track = item.get('track', {})
            if track:
                track_name = track.get('name')
                track_type = track.get('type')
                if track_type != 'track':
                    continue
                track_artists = [artist.get('name') for artist in track.get('artists', []) if artist.get('name')]
                liked_tracks.append({
                    'name': track_name,
                    'artists': track_artists,
                })
        url = data.get('next')

with open('liked.json', 'w', encoding='utf-8') as f:
    json.dump(liked_tracks, f, ensure_ascii=False, indent=4)

# Print statistics
end_time = time.time()
execution_time = end_time - start_time
total_playlist_tracks = sum(len(p['tracks']) for p in all_playlists)
print("\nExport Summary:")
print(f"Playlists: {len(all_playlists)}, Tracks: {total_playlist_tracks}, Liked songs: {len(liked_tracks)}")
print(f"Total time: {execution_time:.2f} seconds")

                
            
    