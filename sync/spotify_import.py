import json
from matching.scorer import score
from clients.spotify_client import SpotifyClient
from sync.batch_processor import BatchProcessor, RateLimiter, create_search_function

def import_spotify(auth_server, state=None, progress_cb=None):
    client = SpotifyClient(auth_server)
    me = client.get("https://api.spotify.com/v1/me").json()

    with open("playlists.json") as f:
        playlists = json.load(f)

    # Initialize batch processor and rate limiter
    # Spotify allows ~180 requests/minute, use 150 to be safe
    batch_processor = BatchProcessor(batch_size=20, max_workers=5)
    rate_limiter = RateLimiter(max_calls=150, time_window=60)
    
    # Create search function for Spotify
    search_func = create_search_function(client, platform='spotify')
    
    # Score function wrapper
    def score_func(track, candidate):
        return score(track["name"], track["artists"], candidate)

    for pl in playlists:
        if state:
            state.current_playlist = pl["name"]
            if progress_cb:
                progress_cb(state)

        # Create playlist
        resp = client.post(
            f"https://api.spotify.com/v1/users/{me['id']}/playlists",
            json={"name": pl["name"], "public": True}
        )
        pid = resp.json()["id"]

        # Process tracks in batches (search + score concurrently)
        batch_results = batch_processor.process_in_batches(
            all_tracks=pl["tracks"],
            search_func=search_func,
            score_func=score_func,
            confidence_threshold=80,
            rate_limiter=rate_limiter
        )

        # Add tracks sequentially to maintain order and respect rate limits
        uris_to_add = []
        for track, best_match, best_score in batch_results:
            if best_match and best_score >= 80:
                uris_to_add.append(best_match['uri'])
                if state:
                    state.added.append(track)
                
                # Add in batches of 100 (Spotify API limit)
                if len(uris_to_add) >= 100:
                    rate_limiter.wait_if_needed()
                    client.post(
                        f"https://api.spotify.com/v1/playlists/{pid}/tracks",
                        json={"uris": uris_to_add}
                    )
                    uris_to_add = []
            else:
                if state:
                    state.failed.append(track)
            
            # Update UI progress
            if state and progress_cb:
                progress_cb(state)
        
        # Add remaining tracks
        if uris_to_add:
            rate_limiter.wait_if_needed()
            client.post(
                f"https://api.spotify.com/v1/playlists/{pid}/tracks",
                json={"uris": uris_to_add}
            )
