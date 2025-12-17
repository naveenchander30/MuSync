import json
from clients.ytmusic_client import YTMusicClient

def export_ytmusic(auth_server, state=None, progress_cb=None):
    client = YTMusicClient(auth_server)
    playlists = []

    for p in client.get_library_playlists():
        name = p["title"]

        if state:
            state.current_playlist = name
            if progress_cb:
                progress_cb(state)

        details = client.get_playlist(p["playlistId"])
        tracks = []

        for t in details["tracks"]:
            tracks.append({
                "name": t["title"],
                "artists": [a["name"] for a in t.get("artists", [])]
            })

        playlists.append({"name": name, "tracks": tracks})

    with open("playlists.json", "w") as f:
        json.dump(playlists, f, indent=2)
