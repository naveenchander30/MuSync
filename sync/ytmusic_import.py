import json
from matching.scorer import score
from clients.ytmusic_client import YTMusicClient

def import_ytmusic(auth_server, state=None, progress_cb=None):
    client = YTMusicClient(auth_server)

    with open("playlists.json") as f:
        playlists = json.load(f)

    existing = {
        p["title"]: p["playlistId"]
        for p in client.get_library_playlists()
    }

    for pl in playlists:
        if state:
            state.current_playlist = pl["name"]
            if progress_cb:
                progress_cb(state)

        pid = existing.get(pl["name"]) or client.create_playlist(pl["name"])

        for tr in pl["tracks"]:
            res = client.search(
                f"{tr['name']} {tr['artists'][0]}",
                limit=5
            )

            best_vid = None
            best_score = 0

            for r in res:
                cand = {
                    "name": r["title"],
                    "artists": [a["name"] for a in r.get("artists", [])],
                    "videoId": r["videoId"]
                }
                s = score(tr["name"], tr["artists"], cand)
                if s > best_score:
                    best_score = s
                    best_vid = cand["videoId"]

            if best_score < 75:
                if state:
                    state.failed.append(tr)
                continue

            client.add_playlist_items(pid, [best_vid])
            if state:
                state.added.append(tr)
