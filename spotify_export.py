import os
import requests
import json
import webbrowser

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
ACCESS_TOKEN = tokens.get('access_token')
SPOTIFY_HEADER={
    "Authorization": f"Bearer {ACCESS_TOKEN}",
}

url="https://api.spotify.com/v1/me"
user_info=requests.get(url,headers=SPOTIFY_HEADER)
if user_info.status_code == 200:
    USER_ID= user_info.json().get('id')

all_playlists = []
url=f"https://api.spotify.com/v1/users/{USER_ID}/playlists"
playlists=requests.get(url,headers=SPOTIFY_HEADER)
if playlists.status_code == 200:
    playlists_data = playlists.json().get('items', [])
    for playlist in playlists_data:
        playlist_info= {
            'name': playlist.get('name'),
            'tracks': [],
        }
        tracks_url=playlist.get('tracks', {}).get('href')
        tracks= requests.get(tracks_url, headers=SPOTIFY_HEADER)
        if tracks.status_code == 200:
            tracks_data = tracks.json().get('items', [])
            for track in tracks_data:
                track_type= track.get('track', {}).get('type')
                track_name=track.get('track', {}).get('name')
                if track_type== 'track':
                    track_artists = ", ".join(artist.get('name') for artist in track.get('track', {}).get('artists', []) if artist.get('name'))
                    playlist_info['tracks'].append({
                        'name': track_name,
                        'artists': track_artists,
                        'type': track_type
                    })
                elif track_type == 'episode':
                    track_show= track.get('track', {}).get('show', {}).get('name')
                    playlist_info['tracks'].append({
                        'name': track_name,
                        'show': track_show,
                        'type': track_type
                    })
        all_playlists.append(playlist_info)
    with open('playlists.json', 'w',encoding='utf-8') as f:
        json.dump(all_playlists, f, ensure_ascii=False,indent=4)
                
            
    