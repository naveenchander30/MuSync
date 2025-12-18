"""
Batch processing utilities for efficient playlist synchronization
Implements batch search and scoring to improve performance
"""
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock


class RateLimiter:
    """Token bucket rate limiter to prevent API throttling"""
    
    def __init__(self, max_calls, time_window=60):
        """
        Args:
            max_calls: Maximum number of calls allowed in time_window
            time_window: Time window in seconds (default: 60s)
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = Lock()
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        with self.lock:
            now = time.time()
            # Remove calls outside the time window
            self.calls = [call_time for call_time in self.calls 
                         if now - call_time < self.time_window]
            
            if len(self.calls) >= self.max_calls:
                # Calculate wait time
                oldest_call = min(self.calls)
                wait_time = self.time_window - (now - oldest_call)
                if wait_time > 0:
                    time.sleep(wait_time + 0.1)  # Add small buffer
                    # Clean up again after waiting
                    now = time.time()
                    self.calls = [call_time for call_time in self.calls 
                                 if now - call_time < self.time_window]
            
            self.calls.append(now)


class BatchProcessor:
    """Process tracks in batches with concurrent search and scoring"""
    
    def __init__(self, batch_size=20, max_workers=5):
        """
        Args:
            batch_size: Number of tracks to process per batch
            max_workers: Number of concurrent worker threads
        """
        self.batch_size = batch_size
        self.max_workers = max_workers
    
    def process_tracks_batch(self, tracks, search_func, score_func, 
                            confidence_threshold=75, rate_limiter=None):
        """
        Process tracks in batch with concurrent search and scoring
        
        Args:
            tracks: List of track dictionaries with 'name' and 'artists'
            search_func: Function to search for candidates (takes track dict)
            score_func: Function to score candidates (takes track and candidate)
            confidence_threshold: Minimum score to consider a match
            rate_limiter: Optional RateLimiter instance
            
        Returns:
            List of tuples: (track, best_match, score) or (track, None, 0) if no match
        """
        results = []
        
        def search_and_score(track):
            """Search and score a single track"""
            try:
                # Apply rate limiting if provided
                if rate_limiter:
                    rate_limiter.wait_if_needed()
                
                # Search for candidates
                candidates = search_func(track)
                
                if not candidates:
                    return (track, None, 0)
                
                # Score all candidates
                best_match = None
                best_score = 0
                
                for candidate in candidates:
                    score = score_func(track, candidate)
                    if score > best_score:
                        best_score = score
                        best_match = candidate
                
                # Check if score meets threshold
                if best_score < confidence_threshold:
                    return (track, None, best_score)
                
                return (track, best_match, best_score)
                
            except Exception as e:
                print(f"Error processing track {track.get('name', 'Unknown')}: {e}")
                return (track, None, 0)
        
        # Process tracks concurrently
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tracks in the batch
            future_to_track = {
                executor.submit(search_and_score, track): track 
                for track in tracks
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_track):
                result = future.result()
                results.append(result)
        
        # Sort results to maintain original order
        track_order = {id(track): idx for idx, track in enumerate(tracks)}
        results.sort(key=lambda x: track_order.get(id(x[0]), float('inf')))
        
        return results
    
    def process_in_batches(self, all_tracks, search_func, score_func,
                          confidence_threshold=75, rate_limiter=None,
                          progress_callback=None):
        """
        Process all tracks in batches
        
        Args:
            all_tracks: Complete list of tracks to process
            search_func: Function to search for candidates
            score_func: Function to score candidates
            confidence_threshold: Minimum score to consider a match
            rate_limiter: Optional RateLimiter instance
            progress_callback: Optional callback for progress updates
            
        Yields:
            Tuples of (track, best_match, score)
        """
        total_tracks = len(all_tracks)
        processed = 0
        
        # Process in batches
        for i in range(0, total_tracks, self.batch_size):
            batch = all_tracks[i:i + self.batch_size]
            batch_results = self.process_tracks_batch(
                batch, 
                search_func, 
                score_func,
                confidence_threshold,
                rate_limiter
            )
            
            # Yield results one by one
            for result in batch_results:
                processed += 1
                if progress_callback:
                    progress_callback(processed, total_tracks)
                yield result


def create_search_function(client, platform='spotify'):
    """
    Create a search function wrapper for a specific platform
    
    Args:
        client: SpotifyClient or YTMusicClient instance
        platform: 'spotify' or 'ytmusic'
        
    Returns:
        Function that takes track dict and returns list of candidates
    """
    def search_spotify(track):
        """Search Spotify for track"""
        query = f"{track['name']} {track['artists'][0]}"
        try:
            resp = client.get(
                f"https://api.spotify.com/v1/search?q={query}&type=track&limit=5"
            )
            data = resp.json()
            
            candidates = []
            for item in data.get('tracks', {}).get('items', []):
                candidates.append({
                    'name': item['name'],
                    'artists': [a['name'] for a in item['artists']],
                    'uri': item['uri']
                })
            return candidates
        except Exception as e:
            print(f"Spotify search error: {e}")
            return []
    
    def search_ytmusic(track):
        """Search YouTube Music for track"""
        query = f"{track['name']} {track['artists'][0]}"
        try:
            results = client.search(query, limit=5)
            
            candidates = []
            for r in results:
                candidates.append({
                    'name': r['title'],
                    'artists': [a['name'] for a in r.get('artists', [])],
                    'videoId': r['videoId']
                })
            return candidates
        except Exception as e:
            print(f"YTMusic search error: {e}")
            return []
    
    return search_spotify if platform == 'spotify' else search_ytmusic
