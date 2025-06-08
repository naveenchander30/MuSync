from flask import Flask, redirect, request, jsonify
import json,urllib.parse,base64
import os,requests,time,secrets
from google_auth_oauthlib.flow import Flow

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
STATE = secrets.token_urlsafe(16)  # Generate a random state token

SCOPES = [
        "https://www.googleapis.com/auth/youtube",
        "https://www.googleapis.com/auth/youtube.force-ssl"
    ]


app = Flask(__name__)
app.secret_key=secrets.token_urlsafe(64)

@app.route('/')
def index():
    return "Welcome to the MuSync Auth Service!"

@app.route('/spotify/login', methods=['GET'])
def spotify_auth():
    params={
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": "https://musync-k60r.onrender.com/spotify/callback",
        "scope": "playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private user-library-read user-library-modify user-read-private user-read-email",
        "state": STATE
    }
    url= "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(params)
    return redirect(url)

@app.route('/spotify/callback', methods=['GET'])
def spotify_callback():
        code=request.args.get('code')
        received_state = request.args.get('state')
        
        if received_state != STATE:
            return jsonify({"error": "Invalid state parameter"}), 400
        token_url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        params = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "https://musync-k60r.onrender.com/spotify/callback"
        }
        
        response=requests.post(token_url,headers=headers, data=params)
        if response.status_code == 200:
            data=response.json()
            access_token = data.get('access_token')
            refresh_token = data.get('refresh_token')
            expiry = data.get('expires_in')
            tokens = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expiry": time.time() + expiry
            }
            with open('spotify_tokens.json', 'w') as f:
                json.dump(tokens, f)
        return "Authentication successful! You can close this window."
    
@app.route('/spotify/tokens', methods=['GET'])
def get_spotify_tokens():
    with open('spotify_tokens.json', 'r') as f:
        tokens = json.load(f)
    return jsonify(tokens)

@app.route('/ytmusic/login') 
def ytmusic_login():
    flow = Flow.from_client_secrets_file(
        "client.json",
        scopes=SCOPES,
        redirect_uri="https://https://musync-k60r.onrender.com/ytmusic/callback"
    )
    auth_url, state = flow.authorization_url(prompt="consent")
    session["state"] = state
    return redirect(auth_url)
    
@app.route('ytmusic/callback') 
def ytmusic_callback():
    state=session['state']
    flow = Flow.from_client_secrets_file(
        "client.json",
        scopes=SCOPES,
        state=state,
        redirect_uri="https://https://musync-k60r.onrender.com/ytmusic/callback"
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    auth_headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json",
        "X-Goog-AuthUser": "0",
        "x-origin": "https://music.youtube.com"
    }
    with open("auth.json",'w') as f:
        json.dump(auth_headers,f)
    return "Authentication successful! You can close this window."

    
@app.route('/ytmusic/tokens', methods=['GET'])
def get_ytmusic_tokens():
    with open("auth.json", "r") as f:
        auth_headers = json.load(f)
    return jsonify(auth_headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True, port=int(os.getenv("PORT", 8080)))
