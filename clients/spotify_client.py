import requests

class SpotifyClient:
    def __init__(self, auth_server):
        self.auth_server = auth_server
        self.headers = self._headers()

    def _headers(self):
        token = requests.get(f"{self.auth_server}/spotify/token").json()
        return {"Authorization": f"Bearer {token['access_token']}"}

    def get(self, url):
        r = requests.get(url, headers=self.headers)
        if r.status_code == 401:
            self.headers = self._headers()
            r = requests.get(url, headers=self.headers)
        return r

    def post(self, url, json=None):
        return requests.post(url, headers=self.headers, json=json)
