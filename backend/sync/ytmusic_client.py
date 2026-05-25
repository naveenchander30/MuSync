from ytmusicapi import YTMusic
from backend.auth.token_manager import TokenManager
from backend.sync.rate_limiter import RateLimiter


class YTMusicClient:
    """YouTube Music API client with automatic token refresh and rate limiting"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.rate_limiter = RateLimiter(max_calls=100, period_seconds=60)
        self._ytmusic = None
    
    def _get_ytmusic(self):
        """Get authenticated YTMusic instance"""
        if self._ytmusic is None:
            access_token = TokenManager.get_access_token(self.user_id, 'ytmusic')
            
            # Initialize with auth headers
            self._ytmusic = YTMusic()
            self._ytmusic.headers.update({
                "Authorization": f"Bearer {access_token}",
                "X-Origin": "https://music.youtube.com"
            })
        
        return self._ytmusic
    
    def _make_request(self, method_name: str, *args, **kwargs):
        """Make API request with retry logic"""
        self.rate_limiter.wait_if_needed()
        
        ytmusic = self._get_ytmusic()
        
        try:
            method = getattr(ytmusic, method_name)
            return method(*args, **kwargs)
        except Exception as e:
            # Try to refresh token and retry once
            try:
                TokenManager.refresh_youtube_token(self.user_id)
                self._ytmusic = None  # Reset instance
                ytmusic = self._get_ytmusic()
                method = getattr(ytmusic, method_name)
                return method(*args, **kwargs)
            except Exception as retry_e:
                raise Exception(f"YouTube Music API error: {str(retry_e)}")
    
    def get_playlists(self):
        """Get all user playlists"""
        return self._make_request('get_library_playlists')
    
    def get_playlist(self, playlist_id: str):
        """Get playlist details and tracks"""
        return self._make_request('get_playlist', playlist_id)
    
    def search(self, query: str, filter: str = "songs", limit=20):
        """Search for tracks"""
        return self._make_request('search', query, filter, limit)
    
    def create_playlist(self, title: str, description: str = "", privacy_status: str = "PRIVATE"):
        """Create a new playlist"""
        return self._make_request(
            'create_playlist',
            title=title,
            description=description,
            privacy_status=privacy_status
        )
    
    def add_playlist_items(self, playlist_id: str, video_ids: list):
        """Add videos to a playlist"""
        return self._make_request(
            'add_playlist_items',
            playlist_id,
            video_ids
        )
    
    def get_library_songs(self, limit=50):
        """Get library songs"""
        return self._make_request('get_library_songs', limit)
