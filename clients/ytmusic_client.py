import json
import requests
from ytmusicapi import YTMusic
import time

class YTMusicClient:
    def __init__(self, auth_server, auth_file="auth.json"):
        self.auth_server = auth_server
        self.auth_file = auth_file
        self.max_retries = 3
        self.refresh_auth()
        self.ytmusic = YTMusic(self.auth_file)

    def refresh_auth(self):
        try:
            resp = requests.get(f"{self.auth_server}/ytmusic/token", timeout=30)
            resp.raise_for_status()
            with open(self.auth_file, "w") as f:
                json.dump(resp.json(), f)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to refresh YouTube Music auth: {e}")
        except IOError as e:
            raise Exception(f"Failed to write auth file: {e}")

    def _retry(self, func, *args):
        for attempt in range(self.max_retries):
            try:
                return func(*args)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"YouTube Music API request failed after {self.max_retries} attempts: {e}")
                try:
                    self.refresh_auth()
                    self.ytmusic = YTMusic(self.auth_file)
                    time.sleep(2 ** attempt)  # Exponential backoff
                except Exception:
                    if attempt == self.max_retries - 1:
                        raise
                    time.sleep(2 ** attempt)

    def get_library_playlists(self):
        return self._retry(self.ytmusic.get_library_playlists)

    def get_playlist(self, pid):
        return self._retry(self.ytmusic.get_playlist, pid)

    def search(self, q, limit=5):
        return self._retry(self.ytmusic.search, q, "songs", limit)

    def create_playlist(self, name, desc=""):
        return self._retry(self.ytmusic.create_playlist, name, desc)

    def add_playlist_items(self, pid, vids):
        return self._retry(self.ytmusic.add_playlist_items, pid, vids)

    def get_liked_songs(self):
        return self._retry(self.ytmusic.get_liked_songs)
