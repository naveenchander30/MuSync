import os
import requests
import json
import webbrowser

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

webbrowser.open(f"http://127.0.0.1:8080/spotify/login")

def wait_for_callback():
    print("Waiting for Spotify callback...")
    input("Press Enter after the callback is received...")
    
wait_for_callback()

with open('tokens.json', 'r') as f:
    tokens = json.load(f)
ACCESS_TOKEN = tokens.get('access_token')
SPOTIFY_HEADER={
    "Authorization": f"Bearer {ACCESS_TOKEN}",
}

url="https://api.spotify.com/v1/me"
user_info=requests.get(url,headers=SPOTIFY_HEADER)
if user_info.status_code == 200:
    USER_ID= user_info.json().get('id')
    
with open('playlists.json', 'r', encoding='utf-8') as f:
    all_playlists = json.load(f)
url=f"https://api.spotify.com/v1/me/playlists?limit=50"
existing_playlist_names = {}
while url:
    existing_playlists = requests.get(url, headers=SPOTIFY_HEADER)
    if existing_playlists.status_code == 200:
        existing_playlists_data = existing_playlists.json().get('items', [])
        existing_playlist_names.update({playlist.get('name'):playlist.get('id') for playlist in existing_playlists_data})
        next_url = existing_playlists.json().get('next')
        url = next_url if next_url else None
for playlist in all_playlists:
    playlist_name= playlist.get('name')
    tracks = playlist.get('tracks', [])
    if playlist_name in existing_playlist_names:
        url = f"https://api.spotify.com/v1/playlists/{existing_playlist_names[playlist_name]}/tracks?limit=50"
        existing_track_uris=[]
        while url:
            existing_tracks = requests.get(url, headers=SPOTIFY_HEADER)
            if existing_tracks.status_code == 200:
                existing_tracks_data = existing_tracks.json().get('items', [])
                existing_track_uris.extend([item.get('track', {}).get('uri') for item in existing_tracks_data if item.get('track')])
                next_url = existing_tracks.json().get('next')
                url = next_url if next_url else None
        for track in tracks:
            track_type = track.get('type')
            track_name = track.get('name')
            track_artists = []
            track_show = ""
            
            if track_type == 'track':
                track_artists = track.get('artists', [])
                track_show = ""
            elif track_type == 'episode':
                track_show = track.get('show', "")
                track_artists = [""]
            
            url= f"https://api.spotify.com/v1/search"
            params = {
                'q': f"{track_name} {' '.join(track_artists)} {track_show}",
                'type': track_type,
                'limit': 1
            }
            search_response = requests.get(url, headers=SPOTIFY_HEADER, params=params)
            if search_response.status_code == 200:
                search_data = search_response.json()
                if track_type == 'track':
                    track_uri = search_data.get('tracks', {}).get('items', [{}])[0].get('uri')
                elif track_type == 'episode':
                    track_uri = search_data.get('episodes', {}).get('items', [{}])[0].get('uri')
                if track_uri and track_uri not in existing_track_uris:
                    add_url = f"https://api.spotify.com/v1/playlists/{existing_playlist_names[playlist_name]}/tracks"
                    data = {
                        'uris': [track_uri]
                    }
                    add_response = requests.post(add_url, headers=SPOTIFY_HEADER, json=data)
    else:  
        url = f"https://api.spotify.com/v1/users/{USER_ID}/playlists"
        data={
            'name': playlist_name,
            'public': True
        }
        response= requests.post(url,headers=SPOTIFY_HEADER, json=data)
        if response.status_code == 201:
            playlist_id = response.json().get('id')
            for track in tracks:
                track_type = track.get('type')
                track_name = track.get('name')
                track_artists = []
                track_show = ""
                
                if track_type == 'track':
                    track_artists = track.get('artists', [])
                    track_show = ""
                elif track_type == 'episode':
                    track_show = track.get('show', "")
                    track_artists = [""]
                
                url= f"https://api.spotify.com/v1/search"
                params = {
                    'q': f"{track_name} {' '.join(track_artists)} {track_show}",
                    'type': track_type,
                    'limit': 1
                }
                search_response = requests.get(url, headers=SPOTIFY_HEADER, params=params)
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    if track_type == 'track':
                        track_uri = search_data.get('tracks', {}).get('items', [{}])[0].get('uri')
                    elif track_type == 'episode':
                        track_uri = search_data.get('episodes', {}).get('items', [{}])[0].get('uri')
                    if track_uri:
                        add_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
                        data = {
                            'uris': [track_uri]
                        }
                        add_response = requests.post(add_url, headers=SPOTIFY_HEADER, json=data)
                    
                
