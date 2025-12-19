import json
from matching.scorer import score
from clients.ytmusic_client import YTMusicClient
from sync.batch_processor import BatchProcessor, RateLimiter, create_search_function

def import_ytmusic(auth_server, state=None, progress_cb=None):
    import os
    if not os.path.exists("playlists.json"):
        raise FileNotFoundError("playlists.json not found. Please export playlists first.")
    
    client = YTMusicClient(auth_server)

    with open("playlists.json") as f:
        playlists = json.load(f)

    existing = {
        p["title"]: p["playlistId"]
        for p in client.get_library_playlists()
    }

    # Initialize batch processor and rate limiter
    # YouTube Music allows ~100 requests/minute, use 80 to be safe
    batch_processor = BatchProcessor(batch_size=15, max_workers=4)
    rate_limiter = RateLimiter(max_calls=80, time_window=60)
    
    # Create search function for YouTube Music
    search_func = create_search_function(client, platform='ytmusic')
    
    # Score function wrapper
    def score_func(track, candidate):
        return score(track["name"], track["artists"], candidate)

    for pl in playlists:
        if state:
            state.current_playlist = pl["name"]
            if progress_cb:
                progress_cb(state)

        # Get or create playlist
        pid = existing.get(pl["name"]) or client.create_playlist(pl["name"])

        # Process tracks in batches (search + score concurrently)
        batch_results = batch_processor.process_in_batches(
            all_tracks=pl["tracks"],
            search_func=search_func,
            score_func=score_func,
            confidence_threshold=75,
            rate_limiter=rate_limiter
        )

        # Add tracks sequentially to maintain order and respect rate limits
        video_ids_to_add = []
        for track, best_match, best_score in batch_results:
            if best_match and best_score >= 75:
                video_ids_to_add.append(best_match['videoId'])
                if state:
                    state.added.append(track)
                
                # Add in batches of 50 (reasonable size for YTMusic API)
                if len(video_ids_to_add) >= 50:
                    rate_limiter.wait_if_needed()
                    client.add_playlist_items(pid, video_ids_to_add)
                    video_ids_to_add = []
            else:
                if state:
                    state.failed.append(track)
            
            # Update UI progress
            if state and progress_cb:
                progress_cb(state)
        
        # Add remaining tracks
        if video_ids_to_add:
            rate_limiter.wait_if_needed()
            client.add_playlist_items(pid, video_ids_to_add)
