import json
import requests
from ytmusicapi import YTMusic

class YTMusicClient:
    def __init__(self, auth_server, auth_file="auth.json"):
        self.auth_server = auth_server
        self.auth_file = auth_file
        self.refresh_auth()
        self.ytmusic = YTMusic(self.auth_file)

    def refresh_auth(self):
        resp = requests.get(f"{self.auth_server}/ytmusic/token")
        with open(self.auth_file, "w") as f:
            json.dump(resp.json(), f)

    def _retry(self, func, *args):
        try:
            return func(*args)
        except Exception:
            self.refresh_auth()
            self.ytmusic = YTMusic(self.auth_file)
            return func(*args)

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
