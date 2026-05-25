import requests
from backend.auth.token_manager import TokenManager
from backend.sync.rate_limiter import RateLimiter


class SpotifyClient:
    """Spotify API client with automatic token refresh and rate limiting"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.base_url = "https://api.spotify.com/v1"
        self.rate_limiter = RateLimiter(max_calls=100, period_seconds=60)
    
    def _get_headers(self):
        """Get authorization headers with fresh token"""
        access_token = TokenManager.get_access_token(self.user_id, 'spotify')
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs):
        """Make authenticated API request with retry logic"""
        self.rate_limiter.wait_if_needed()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        try:
            response = requests.request(
                method, url, headers=headers, timeout=30, **kwargs
            )
            
            if response.status_code == 401:
                # Token expired, refresh and retry
                TokenManager.refresh_spotify_token(self.user_id)
                headers = self._get_headers()
                response = requests.request(
                    method, url, headers=headers, timeout=30, **kwargs
                )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Spotify API error: {str(e)}")
    
    def get_playlists(self, limit=50):
        """Get all user playlists"""
        playlists = []
        url = f"me/playlists?limit={limit}"
        
        while url:
            data = self._make_request('GET', url)
            playlists.extend(data.get('items', []))
            url = data.get('next')
            if url:
                url = url.replace("https://api.spotify.com/v1/", "")
        
        return playlists
    
    def get_playlist_tracks(self, playlist_id: str):
        """Get all tracks from a playlist"""
        tracks = []
        url = f"playlists/{playlist_id}/tracks?limit=100"
        
        while url:
            data = self._make_request('GET', url)
            tracks.extend(data.get('items', []))
            url = data.get('next')
            if url:
                url = url.replace("https://api.spotify.com/v1/", "")
        
        return tracks
    
    def search_track(self, query: str, limit=5):
        """Search for a track"""
        from urllib.parse import quote
        encoded_query = quote(query)
        return self._make_request('GET', f"search?q={encoded_query}&type=track&limit={limit}")
    
    def create_playlist(self, name: str, description: str = "", public: bool = False):
        """Create a new playlist"""
        return self._make_request(
            'POST', 'me/playlists',
            json={
                "name": name,
                "description": description,
                "public": public
            }
        )
    
    def add_tracks_to_playlist(self, playlist_id: str, track_uris: list):
        """Add tracks to a playlist"""
        return self._make_request(
            'POST', f'playlists/{playlist_id}/tracks',
            json={"uris": track_uris}
        )
