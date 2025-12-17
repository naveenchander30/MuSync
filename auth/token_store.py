import json
import os
import time

class JSONTokenStore:
    """
    Lightweight JSON-backed token store.
    Keeps token refresh logic centralized.
    """

    def __init__(self, path="tokens.json"):
        self.path = path

    def load(self, service):
        if not os.path.exists(self.path):
            return None
        with open(self.path, "r") as f:
            return json.load(f).get(service)

    def save(self, service, token):
        data = {}
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                data = json.load(f)
        data[service] = token
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

    def is_expired(self, token, buffer=60):
        return time.time() > token["expiry"] - buffer
