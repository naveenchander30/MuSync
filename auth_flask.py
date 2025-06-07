from flask import Flask, redirect, request, jsonify
import json,urllib.parse,base64
import os,requests,time,secrets

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
STATE = secrets.token_urlsafe(16)  # Generate a random state token

app = Flask(__name__)

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
        return tokens
@app.route('/spotify/refresh', methods=['POST'])
def refresh_spotify_token():
    refresh_token = request.args.get('refresh_token')
    if not refresh_token:
        return jsonify({"error": "No refresh token found"}), 400
    params = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    }
    token_url = "https://accounts.spotify.com/api/token"
    response = requests.post(token_url, headers=headers, data=params)
    if response.status_code == 200:
        data = response.json()
        access_token = data.get('access_token')
        if 'refresh_token' in data:
            refresh_token = data.get('refresh_token')
        expiry = data.get('expires_in')
        tokens = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expiry": time.time() + expiry
        }
        return tokens
            
if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True, port=int(os.getenv("PORT", 8080)))
