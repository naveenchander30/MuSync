import requests
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlencode
from google_auth_oauthlib.flow import Flow
from flask import redirect, session, current_app

from backend.config import (
    AUTH_BASE_URL, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET,
    GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET,
    SPOTIFY_SCOPES, YT_SCOPES
)
from backend.auth.token_manager import TokenManager
from backend.database import db, User


class OAuthFlows:
    """Handle OAuth authentication flows for Spotify and YouTube Music"""
    
    @staticmethod
    def spotify_login_url():
        """Generate Spotify OAuth URL"""
        state = secrets.token_urlsafe(16)
        session['spotify_state'] = state
        
        params = {
            "client_id": SPOTIFY_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": f"{AUTH_BASE_URL}/auth/spotify/callback",
            "scope": SPOTIFY_SCOPES,
            "state": state
        }
        
        return f"https://accounts.spotify.com/authorize?{urlencode(params)}"
    
    @staticmethod
    def handle_spotify_callback(authorization_code: str, state: str, user_id: str):
        """Handle Spotify OAuth callback and exchange code for tokens"""
        # Verify state
        if state != session.get('spotify_state'):
            raise ValueError("Invalid OAuth state")
        
        # Exchange code for tokens
        resp = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": "Basic " + requests.auth.HTTPBasicAuth(
                    SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
                ).auth_header,
            },
            data={
                "grant_type": "authorization_code",
                "code": authorization_code,
                "redirect_uri": f"{AUTH_BASE_URL}/auth/spotify/callback"
            }
        )
        
        if not resp.ok:
            raise Exception(f"Spotify token exchange failed: {resp.text}")
        
        data = resp.json()
        refresh_token = data["refresh_token"]
        access_token = data["access_token"]
        expires_in = data.get("expires_in", 3600)
        scope = data.get("scope", SPOTIFY_SCOPES)
        expiry = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Save credential
        TokenManager.save_credential(
            user_id=user_id,
            service='spotify',
            refresh_token=refresh_token,
            access_token_expiry=expiry,
            scope=scope
        )
        
        return True
    
    @staticmethod
    def ytmusic_login_url():
        """Generate YouTube Music OAuth URL"""
        # Create Google OAuth flow
        client_config = {
            "web": {
                "client_id": GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": GOOGLE_OAUTH_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [f"{AUTH_BASE_URL}/auth/ytmusic/callback"]
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=YT_SCOPES,
            redirect_uri=f"{AUTH_BASE_URL}/auth/ytmusic/callback"
        )
        
        authorization_url, state = flow.authorization_url(
            prompt='consent',
            access_type='offline',
            include_granted_scopes='true'
        )
        
        session['ytmusic_state'] = state
        return authorization_url
    
    @staticmethod
    def handle_ytmusic_callback(authorization_response: str, state: str, user_id: str):
        """Handle YouTube Music OAuth callback"""
        # Verify state
        if state != session.get('ytmusic_state'):
            raise ValueError("Invalid OAuth state")
        
        # Create Google OAuth flow
        client_config = {
            "web": {
                "client_id": GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": GOOGLE_OAUTH_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [f"{AUTH_BASE_URL}/auth/ytmusic/callback"]
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=YT_SCOPES,
            state=state,
            redirect_uri=f"{AUTH_BASE_URL}/auth/ytmusic/callback"
        )
        
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        
        # Extract tokens
        refresh_token = credentials.refresh_token
        access_token = credentials.token
        expiry = credentials.expiry
        scope = " ".join(credentials.scopes)
        
        # Save credential
        TokenManager.save_credential(
            user_id=user_id,
            service='ytmusic',
            refresh_token=refresh_token,
            access_token_expiry=expiry,
            scope=scope
        )
        
        return True
