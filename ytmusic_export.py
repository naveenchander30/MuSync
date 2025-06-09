from ytmusicapi import YTMusic
import json,requests
import webbrowser

webbrowser.open("https://musync-k60r.onrender.com/ytmusic/login")
def wait_for_callback():
    print("Waiting for YouTube Music callback...")
    input("Press Enter after the callback is received...")
    
wait_for_callback()
response = requests.get('https://musync-k60r.onrender.com/ytmusic/tokens')
if response.status_code == 200:
    auth_headers= response.json()
    with open("auth.json", 'w') as f:
        json.dump(auth_headers, f)

ytmusic= YTMusic("auth.json")
library_playlists = ytmusic.get_library_playlists()
playlist_ids={playlist.get('playlistId'):playlist.get('title') for playlist in library_playlists}
all_playlists = []
for playlist_id, playlist_name in playlist_ids.items():
    playlist_info = {
        'name': playlist_name,
        'tracks': [],
    }
    playlist_details=ytmusic.get_playlist(playlist_id,limit=None)
    for track in playlist_details.get('tracks', []):
        track
