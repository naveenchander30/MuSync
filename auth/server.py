from flask import Flask, redirect, request, jsonify, session
import os, time, base64, secrets, requests, pickle
from urllib.parse import urlencode
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import sys
from pathlib import Path

# Add parent directory to path for imports when running standalone
sys.path.insert(0, str(Path(__file__).parent.parent))

from auth.token_store import JSONTokenStore
import config

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(64)
store = JSONTokenStore()

CLIENT_ID = config.CLIENT_ID
CLIENT_SECRET = config.CLIENT_SECRET
GOOGLE_OAUTH_CLIENT_FILE = config.GOOGLE_OAUTH_CLIENT_FILE

SPOTIFY_SCOPES = (
    "playlist-read-private playlist-read-collaborative "
    "playlist-modify-public playlist-modify-private "
    "user-library-read user-library-modify "
    "user-read-private user-read-email"
)

YT_SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

@app.route("/spotify/login")
def spotify_login():
    session["state"] = secrets.token_urlsafe(16)
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": request.host_url + "spotify/callback",
        "scope": SPOTIFY_SCOPES,
        "state": session["state"]
    }
    return redirect("https://accounts.spotify.com/authorize?" + urlencode(params))

@app.route("/spotify/callback")
def spotify_callback():
    if request.args.get("state") != session.get("state"):
        return "Invalid OAuth state", 400

    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": "Basic " + base64.b64encode(
                f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
            ).decode()
        },
        data={
            "grant_type": "authorization_code",
            "code": request.args.get("code"),
            "redirect_uri": request.host_url + "spotify/callback"
        }
    )

    data = resp.json()
    store.save("spotify", {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "expiry": time.time() + data["expires_in"]
    })

    return "Spotify authentication complete."

def refresh_spotify(refresh_token):
    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": "Basic " + base64.b64encode(
                f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
            ).decode()
        },
        data={"grant_type": "refresh_token", "refresh_token": refresh_token}
    )
    data = resp.json()
    return {
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token", refresh_token),
        "expiry": time.time() + data["expires_in"]
    }

@app.route("/spotify/token")
def spotify_token():
    token = store.load("spotify")
    if not token:
        return jsonify({"error": "Not authenticated. Please visit /spotify/login first."}), 401
    if store.is_expired(token):
        token = refresh_spotify(token["refresh_token"])
        store.save("spotify", token)
    return jsonify({"access_token": token["access_token"]})

@app.route("/ytmusic/login")
def ytmusic_login():
    flow = Flow.from_client_secrets_file(
        GOOGLE_OAUTH_CLIENT_FILE,
        scopes=YT_SCOPES,
        redirect_uri=request.host_url + "ytmusic/callback"
    )
    url, state = flow.authorization_url(prompt="consent")
    session["yt_state"] = state
    return redirect(url)

@app.route("/ytmusic/callback")
def ytmusic_callback():
    flow = Flow.from_client_secrets_file(
        GOOGLE_OAUTH_CLIENT_FILE,
        scopes=YT_SCOPES,
        state=session.get("yt_state"),
        redirect_uri=request.host_url + "ytmusic/callback"
    )
    flow.fetch_token(authorization_response=request.url)
    with open("yt_creds.pkl", "wb") as f:
        pickle.dump(flow.credentials, f)
    return "YouTube Music authentication complete."

@app.route("/ytmusic/token")
def ytmusic_token():
    try:
        with open("yt_creds.pkl", "rb") as f:
            creds = pickle.load(f)
    except FileNotFoundError:
        return jsonify({"error": "Not authenticated. Please visit /ytmusic/login first."}), 401
    
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("yt_creds.pkl", "wb") as f:
            pickle.dump(creds, f)
    return jsonify({
        "Authorization": f"Bearer {creds.token}",
        "x-origin": "https://music.youtube.com"
    })

@app.route("/health")
def health_check():
    """Health check endpoint for Docker and monitoring"""
    return jsonify({
        "status": "healthy",
        "service": "musync-auth-server",
        "version": "1.0.0"
    }), 200

if __name__ == "__main__":
    # Run with production-ready settings
    port = int(os.getenv("PORT", 8080))
    debug = os.getenv("FLASK_ENV", "production") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug)
