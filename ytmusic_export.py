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
        if not track.get('videoId') or not track.get('title'):
            continue
        track_name = track.get('title')
        track_artists = [artist.get('name') for artist in track.get('artists', []) if artist.get('name')]
        playlist_info['tracks'].append({
            'name': track_name,
            'artists': track_artists,
        })
    all_playlists.append(playlist_info)
with open('playlists.json', 'w', encoding='utf-8') as f:
    json.dump(all_playlists, f, ensure_ascii=False, indent=4)

liked_songs = ytmusic.get_liked_songs(limit=None)
liked_tracks = []
tracks= liked_songs.get('tracks', [])
for track in tracks:
    if not track.get('videoId') or not track.get('title'):
        continue
    track_name = track.get('title')
    track_artists = [artist.get('name') for artist in track.get('artists', []) if artist.get('name')]
    liked_tracks.append({
        'name': track_name,
        'artists': track_artists,
    })
with open('liked.json', 'w', encoding='utf-8') as f:
    json.dump(liked_tracks, f, ensure_ascii=False, indent=4)
