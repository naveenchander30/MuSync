from ytmusicapi import YTMusic
import json,requests
import webbrowser
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def best_match(track_name,track_artists,search_results):
    best_score=0
    best_uri=None
    for result in search_results:
        item_name=result.get('title', '')
        name_score = similarity(item_name, track_name)*2
        item_artists = [artist.get('name', '') for artist in result.get('artists', [])]
        matching_artists = sum(1 for a in item_artists if a.lower() in [ta.lower() for ta in track_artists])
        total_score = name_score + matching_artists
        if total_score > best_score:
            best_score = total_score
            best_uri = result.get('videoId')
    return best_uri
    

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
playlist_ids={playlist.get('title'):playlist.get('playlistId') for playlist in library_playlists}

with open('playlists.json', 'r', encoding='utf-8') as f:
    all_playlists = json.load(f)
    
for playlist in all_playlists:
    playlist_name = playlist.get('name')
    if playlist_name not in playlist_ids:
        playlist_id = ytmusic.create_playlist(playlist_name,"")
    else:
        playlist_id = playlist_ids[playlist_name]
        
    tracks = playlist.get('tracks', [])
    
    for track in tracks:
        track_name = track.get('name')
        track_artists = track.get('artists', [])
        if not track_name or not track_artists:
            continue
        search_query = f"{track_name} {track_artists[0]}"
        search_results = ytmusic.search(search_query, filter='songs', limit=10)
        if not search_results:
            continue
        best_uri = best_match(track_name, track_artists, search_results)
        if best_uri:
            try:
                ytmusic.add_playlist_items(playlist_id, [best_uri])
            except:
                pass

with open('liked.json', 'r', encoding='utf-8') as f:
    liked_tracks = json.load(f)
    
for track in liked_tracks:
    track_name = track.get('name')
    track_artists = track.get('artists', [])
    if not track_name or not track_artists:
        continue
    search_query = f"{track_name} {track_artists[0]}"
    search_results = ytmusic.search(search_query, filter='songs', limit=10)
    if not search_results:
        continue
    best_uri = best_match(track_name, track_artists, search_results)
    if best_uri:
        try:
            ytmusic.rate_song(best_uri, 'LIKE')
        except:
            pass
        
