from ytmusicapi import YTMusic
import json, requests
import webbrowser
import time

print("Starting YouTube Music export...")
webbrowser.open("https://musync-k60r.onrender.com/ytmusic/login")
def wait_for_callback():
    print("Waiting for YouTube Music callback...")
    input("Press Enter after the callback is received...")
    
wait_for_callback()
print("Getting authentication tokens...")
response = requests.get('https://musync-k60r.onrender.com/ytmusic/tokens')
if response.status_code == 200:
    auth_headers= response.json()
    with open("auth.json", 'w') as f:
        json.dump(auth_headers, f)
    print("Authentication successful!")
else:
    print(f"Error getting authentication tokens: {response.status_code}")
    exit(1)

ytmusic= YTMusic("auth.json")
start_time = time.time()
print("Fetching playlists...")
print("Fetching playlists...")
library_playlists = ytmusic.get_library_playlists()
print(f"Found {len(library_playlists)} playlists")
playlist_ids={playlist.get('playlistId'):playlist.get('title') for playlist in library_playlists}
all_playlists = []
playlist_count = 0
total_tracks = 0

for playlist_id, playlist_name in playlist_ids.items():
    playlist_count += 1
    print(f"Processing playlist ({playlist_count}/{len(playlist_ids)}): {playlist_name}")
    
    playlist_info = {
        'name': playlist_name,
        'tracks': [],
    }
    try:
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
            total_tracks += 1
            
    except Exception as e:
        print(f"Error processing playlist {playlist_name}: {str(e)}")
        
    all_playlists.append(playlist_info)
with open('playlists.json', 'w', encoding='utf-8') as f:
    json.dump(all_playlists, f, ensure_ascii=False, indent=4)

print("\nExporting liked songs...")
liked_songs = ytmusic.get_liked_songs(limit=None)
liked_tracks = []
tracks= liked_songs.get('tracks', [])
print(f"Found {len(tracks)} liked songs")

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

# Print summary
end_time = time.time()
execution_time = end_time - start_time
print("\nExport Summary:")
print(f"Playlists: {len(all_playlists)}, Tracks: {total_tracks}, Liked songs: {len(liked_tracks)}")
print(f"Total time: {execution_time:.2f} seconds")
