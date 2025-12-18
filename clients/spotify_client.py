import requests
import time

class SpotifyClient:
    def __init__(self, auth_server):
        self.auth_server = auth_server
        self.headers = self._headers()
        self.max_retries = 3

    def _headers(self):
        try:
            resp = requests.get(f"{self.auth_server}/spotify/token", timeout=30)
            resp.raise_for_status()
            token = resp.json()
            return {"Authorization": f"Bearer {token['access_token']}"}
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get Spotify token: {e}")

    def get(self, url):
        for attempt in range(self.max_retries):
            try:
                r = requests.get(url, headers=self.headers, timeout=30)
                if r.status_code == 401:
                    self.headers = self._headers()
                    r = requests.get(url, headers=self.headers, timeout=30)
                r.raise_for_status()
                return r
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"Spotify API request failed after {self.max_retries} attempts: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
        return None

    def post(self, url, json=None):
        for attempt in range(self.max_retries):
            try:
                r = requests.post(url, headers=self.headers, json=json, timeout=30)
                if r.status_code == 401:
                    self.headers = self._headers()
                    r = requests.post(url, headers=self.headers, json=json, timeout=30)
                r.raise_for_status()
                return r
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"Spotify API request failed after {self.max_retries} attempts: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
        return None
