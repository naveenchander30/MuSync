import json
from clients.spotify_client import SpotifyClient

def export_spotify(auth_server, state=None, progress_cb=None):
    client = SpotifyClient(auth_server)
    playlists = []
    url = "https://api.spotify.com/v1/me/playlists?limit=50"

    while url:
        data = client.get(url).json()
        for p in data["items"]:
            playlist = {"name": p["name"], "tracks": []}

            if state:
                state.current_playlist = p["name"]
                if progress_cb:
                    progress_cb(state)

            turl = p["tracks"]["href"]
            while turl:
                tdata = client.get(turl).json()
                for it in tdata["items"]:
                    tr = it.get("track")
                    if tr:
                        playlist["tracks"].append({
                            "name": tr["name"],
                            "artists": [a["name"] for a in tr["artists"]]
                        })
                turl = tdata["next"]

            playlists.append(playlist)
        url = data["next"]

    with open("playlists.json", "w") as f:
        json.dump(playlists, f, indent=2)
