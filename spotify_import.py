import os
import requests
import json
import webbrowser
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

webbrowser.open(f"https://musync-k60r.onrender.com/spotify/login")

def wait_for_callback():
    print("Waiting for Spotify callback...")
    input("Press Enter after the callback is received...")

wait_for_callback()
response= requests.get('https://musync-k60r.onrender.com/spotify/tokens')
if response.status_code == 200:
    tokens = response.json()
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
            
            if track_type == 'track':
                track_artists = track.get('artists', [])
            elif track_type == 'episode':
                track_show = track.get('show', "")
            
            url= f"https://api.spotify.com/v1/search"
            params = {
                'q': f"{track_name}",
                'type': track_type,
                'limit': 10
            }
            search_response = requests.get(url, headers=SPOTIFY_HEADER, params=params)
            if search_response.status_code == 200:
                search_data = search_response.json()
                tracks_data= search_data.get('tracks', {}).get('items', [])
                episodes_data = search_data.get('episodes', {}).get('items', [])
                track_uri = None
                best_score = 0
                best_uri = None
                if track_type == 'track' and tracks_data:
                    for item in tracks_data:
                        item_name = item.get('name', '')
                        name_score = similarity(item_name, track_name)

                        item_artists = [artist.get('name', '') for artist in item.get('artists', [])]
                        matching_artists = sum(1 for a in item_artists if a.lower() in [ta.lower() for ta in track_artists])
                        total_score = name_score + matching_artists

                        if total_score > best_score:
                            best_score = total_score
                            best_uri = item.get('uri')

                    track_uri = best_uri

                elif track_type == 'episode' and episodes_data:
                    for item in episodes_data:
                        item_name = item.get('name', '')
                        item_show = item.get('show', {}).get('name', '')
                        if similarity(item_name, track_name) > 0.8 and similarity(item_show, track_show) > 0.8:
                            track_uri = item.get('uri')
                            break
                    
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
                
                if track_type == 'track':
                    track_artists = track.get('artists', [])
                elif track_type == 'episode':
                    track_show = track.get('show', "")
                
                url= f"https://api.spotify.com/v1/search"
                params = {
                    'q': f"{track_name}",
                    'type': track_type,
                    'limit': 10
                }
                search_response = requests.get(url, headers=SPOTIFY_HEADER, params=params)
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    tracks_data= search_data.get('tracks', {}).get('items', [])
                    episodes_data = search_data.get('episodes', {}).get('items', [])
                    track_uri = None
                    best_score = 0
                    best_uri = None
                    if track_type == 'track' and tracks_data:
                        for item in tracks_data:
                            item_name = item.get('name', '')
                            name_score = similarity(item_name, track_name)

                            item_artists = [artist.get('name', '') for artist in item.get('artists', [])]
                            matching_artists = sum(1 for a in item_artists if a.lower() in [ta.lower() for ta in track_artists])
                            total_score = name_score + matching_artists

                            if total_score > best_score:
                                best_score = total_score
                                best_uri = item.get('uri')

                        track_uri = best_uri

                    elif track_type == 'episode' and episodes_data:
                        for item in episodes_data:
                            item_name = item.get('name', '')
                            item_show = item.get('show', {}).get('name', '')
                            if similarity(item_name, track_name) > 0.8 and similarity(item_show, track_show) > 0.8:
                                track_uri = item.get('uri')
                                break
                    add_response = requests.post(add_url, headers=SPOTIFY_HEADER, json=data)
                        
                
