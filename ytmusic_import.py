from ytmusicapi import YTMusic
import json, requests
import webbrowser
import time
from difflib import SequenceMatcher
import re

def clean_playlist_name(name):
    return re.sub(r'[<>:"/\\|?*]', '', name)

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def best_match(track_name, track_artists, search_results):
    best_score = 0
    best_uri = None
    for result in search_results:
        item_name = result.get('title', '')
        name_score = similarity(item_name, track_name) * 2
        item_artists = [artist.get('name', '') for artist in result.get('artists', [])]
        matching_artists = sum(1 for a in item_artists if a.lower() in [ta.lower() for ta in track_artists])
        total_score = name_score + matching_artists
        if total_score > best_score:
            best_score = total_score
            best_uri = result.get('videoId')
    return best_uri

print("Starting YouTube Music import...")
webbrowser.open("https://musync-k60r.onrender.com/ytmusic/login")

def wait_for_callback():
    print("Waiting for YouTube Music callback...")
    input("Press Enter after the callback is received...")
    
wait_for_callback()
print("Getting authentication tokens...")
response = requests.get('https://musync-k60r.onrender.com/ytmusic/tokens')
if response.status_code == 200:
    auth_headers = response.json()
    with open("auth.json", 'w') as f:
        json.dump(auth_headers, f)
    print("Authentication successful!")
else:
    print(f"Error getting authentication tokens: {response.status_code}")
    exit(1)

print("Initializing YouTube Music API...")
ytmusic = YTMusic("auth.json")
start_time = time.time()

print("Getting library playlists...")
library_playlists = ytmusic.get_library_playlists()
playlist_ids = {playlist.get('title'): playlist.get('playlistId') for playlist in library_playlists}
print(f"Found {len(playlist_ids)} existing playlists")

print("Loading playlists from file...")
with open('playlists.json', 'r', encoding='utf-8') as f:
    all_playlists = json.load(f)

# Track statistics
added_tracks = 0
skipped_tracks = 0
not_found_tracks = 0
total_tracks = sum(len(playlist.get('tracks', [])) for playlist in all_playlists)

for i, playlist in enumerate(all_playlists, 1):
    playlist_name = playlist.get('name')
    tracks = playlist.get('tracks', [])
    print(f"\nProcessing playlist ({i}/{len(all_playlists)}): {playlist_name} - {len(tracks)} tracks")
    
    if playlist_name not in playlist_ids:
        print(f"Creating new playlist: {playlist_name}")
        try:
            playlist_id = ytmusic.create_playlist(clean_playlist_name(playlist_name), "")
            print(f"Created playlist with ID: {playlist_id}")
        except Exception as e:
            print(f"Error creating playlist: {str(e)}")
            continue
    else:
        print(f"Playlist already exists, adding tracks")
        playlist_id = playlist_ids[playlist_name]
        try:
            existing_tracks = ytmusic.get_playlist(playlist_id, limit=None)
            existing_track_ids = [track.get('videoId') for track in existing_tracks.get('tracks', []) if track.get('videoId')]
            print(f"Found {len(existing_track_ids)} existing tracks in playlist")
        except Exception as e:
            print(f"Error getting existing tracks: {str(e)}")
            existing_track_ids = []
    
    
    for track in tracks:
        track_name = track.get('name')
        track_artists = track.get('artists', [])
        artists_str = ", ".join(track_artists) if track_artists else "Unknown"
        
        if not track_name or not track_artists:
            print(f"  SKIPPING: Missing name or artists")
            skipped_tracks += 1
            continue
            
        search_query = f"{track_name} {track_artists[0]}"
        try:
            search_results = ytmusic.search(search_query, filter='songs', limit=10)
        except Exception as e:
            print(f"  ERROR SEARCHING: \"{track_name}\" by {artists_str} - {str(e)}")
            continue
            
        if not search_results:
            print(f"  NOT FOUND: \"{track_name}\" by {artists_str}")
            not_found_tracks += 1
            continue
            
        best_uri = best_match(track_name, track_artists, search_results)
        if not best_uri:
            print(f"  NO MATCH: \"{track_name}\" by {artists_str}")
            not_found_tracks += 1
            continue
            
        if best_uri in existing_track_ids:
            skipped_tracks += 1
            continue
            
        try:
            ytmusic.add_playlist_items(playlist_id, [best_uri])
            added_tracks += 1
        except Exception as e:
            print(f"  ERROR ADDING: \"{track_name}\" by {artists_str} - {str(e)}")

print("\nProcessing liked songs...")
with open('liked.json', 'r', encoding='utf-8') as f:
    liked_tracks = json.load(f)
print(f"Found {len(liked_tracks)} liked songs to import")

# Liked songs statistics
liked_added = 0
liked_skipped = 0
liked_not_found = 0

for i, track in enumerate(liked_tracks, 1):
    track_name = track.get('name')
    track_artists = track.get('artists', [])
    artists_str = ", ".join(track_artists) if track_artists else "Unknown"
    
    if not track_name or not track_artists:
        liked_skipped += 1
        continue
        
    search_query = f"{track_name} {track_artists[0]}"
    try:
        search_results = ytmusic.search(search_query, filter='songs', limit=10)
    except Exception as e:
        print(f"  ERROR SEARCHING: \"{track_name}\" by {artists_str} - {str(e)}")
        continue
        
    if not search_results:
        print(f"  NOT FOUND: \"{track_name}\" by {artists_str}")
        liked_not_found += 1
        continue
        
    best_uri = best_match(track_name, track_artists, search_results)
    if not best_uri:
        print(f"  NO MATCH: \"{track_name}\" by {artists_str}")
        liked_not_found += 1
        continue
        
    try:
        ytmusic.rate_song(best_uri, 'LIKE')
        liked_added += 1
    except Exception as e:
        print(f"  ERROR LIKING: \"{track_name}\" by {artists_str} - {str(e)}")
        tracl_skipped += 1

# Print summary
end_time = time.time()
execution_time = end_time - start_time
print("\nImport Summary:")
print(f"Playlists processed: {len(all_playlists)}")
print(f"Playlist tracks: {added_tracks} added, {skipped_tracks} skipped, {not_found_tracks} not found")
print(f"Liked tracks: {liked_added} added, {liked_skipped} skipped, {liked_not_found} not found")
print(f"Total time: {execution_time:.2f} seconds")
