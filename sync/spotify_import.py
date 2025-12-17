import json
from matching.scorer import score
from clients.spotify_client import SpotifyClient

def import_spotify(auth_server, state=None, progress_cb=None):
    client = SpotifyClient(auth_server)
    me = client.get("https://api.spotify.com/v1/me").json()

    with open("playlists.json") as f:
        playlists = json.load(f)

    for pl in playlists:
        if state:
            state.current_playlist = pl["name"]
            if progress_cb:
                progress_cb(state)

        resp = client.post(
            f"https://api.spotify.com/v1/users/{me['id']}/playlists",
            json={"name": pl["name"], "public": True}
        )
        pid = resp.json()["id"]

        for tr in pl["tracks"]:
            q = f"{tr['name']} {tr['artists'][0]}"
            res = client.get(
                f"https://api.spotify.com/v1/search?q={q}&type=track&limit=5"
            ).json()

            best_uri = None
            best_score = 0

            for item in res["tracks"]["items"]:
                cand = {
                    "name": item["name"],
                    "artists": [a["name"] for a in item["artists"]],
                    "uri": item["uri"]
                }
                s = score(tr["name"], tr["artists"], cand)
                if s > best_score:
                    best_score = s
                    best_uri = cand["uri"]

            if best_score < 80:
                if state:
                    state.failed.append(tr)
                continue

            client.post(
                f"https://api.spotify.com/v1/playlists/{pid}/tracks",
                json={"uris": [best_uri]}
            )

            if state:
                state.added.append(tr)
