import requests
import time
from datetime import datetime, timedelta, timezone
from backend.database import db, Credential
from backend.auth.encryption import encryptor
from backend.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


class TokenManager:
    """Handle OAuth token refresh and validation"""
    
    @staticmethod
    def save_credential(user_id: str, service: str, refresh_token: str, 
                       access_token_expiry: datetime = None, scope: str = None):
        """Save or update credential in database"""
        encrypted_token = encryptor.encrypt(refresh_token)
        
        credential = Credential.query.filter_by(
            user_id=user_id, service=service
        ).first()
        
        if credential:
            credential.refresh_token_encrypted = encrypted_token
            credential.access_token_expiry = access_token_expiry
            credential.scope = scope
            credential.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            credential = Credential(
                user_id=user_id,
                service=service,
                refresh_token_encrypted=encrypted_token,
                access_token_expiry=access_token_expiry,
                scope=scope
            )
            db.session.add(credential)
        
        db.session.commit()
        return credential
    
    @staticmethod
    def get_credential(user_id: str, service: str) -> Credential:
        """Get credential from database"""
        return Credential.query.filter_by(
            user_id=user_id, service=service
        ).first()
    
    @staticmethod
    def get_refresh_token(user_id: str, service: str) -> str:
        """Get decrypted refresh token"""
        credential = TokenManager.get_credential(user_id, service)
        if not credential:
            return None
        return encryptor.decrypt(credential.refresh_token_encrypted)
    
    @staticmethod
    def is_token_valid(user_id: str, service: str) -> bool:
        """Check if token exists and is not expired"""
        credential = TokenManager.get_credential(user_id, service)
        if not credential:
            return False
        
        if not credential.access_token_expiry:
            return False
        
        # Token valid if expiry > 5 minutes from now
        expiry_buffer = timedelta(minutes=5)
        return credential.access_token_expiry > (datetime.now(timezone.utc).replace(tzinfo=None) - expiry_buffer)
    
    @staticmethod
    def refresh_spotify_token(user_id: str):
        """Refresh Spotify access token"""
        refresh_token = TokenManager.get_refresh_token(user_id, 'spotify')
        if not refresh_token:
            raise ValueError("No refresh token found for Spotify")
        
        resp = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": "Basic " + requests.auth.HTTPBasicAuth(
                    SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
                ).auth_header,
            },
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
        )
        
        if not resp.ok:
            raise Exception(f"Token refresh failed: {resp.text}")
        
        data = resp.json()
        access_token = data["access_token"]
        expires_in = data.get("expires_in", 3600)
        new_refresh_token = data.get("refresh_token", refresh_token)
        expiry = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(seconds=expires_in)
        
        # Update credential
        TokenManager.save_credential(
            user_id=user_id,
            service='spotify',
            refresh_token=new_refresh_token,
            access_token_expiry=expiry
        )
        
        return access_token
    
    @staticmethod
    def refresh_youtube_token(user_id: str):
        """Refresh YouTube Music access token"""
        refresh_token = TokenManager.get_refresh_token(user_id, 'ytmusic')
        if not refresh_token:
            raise ValueError("No refresh token found for YouTube Music")
        
        # Reconstruct Google credentials
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        )
        
        creds.refresh(Request())
        
        access_token = creds.token
        expiry = creds.expiry
        
        # Update credential
        TokenManager.save_credential(
            user_id=user_id,
            service='ytmusic',
            refresh_token=refresh_token,
            access_token_expiry=expiry
        )
        
        return access_token
    
    @staticmethod
    def get_access_token(user_id: str, service: str) -> str:
        """Get valid access token, refresh if needed"""
        if not TokenManager.is_token_valid(user_id, service):
            if service == 'spotify':
                return TokenManager.refresh_spotify_token(user_id)
            elif service == 'ytmusic':
                return TokenManager.refresh_youtube_token(user_id)
            else:
                raise ValueError(f"Unknown service: {service}")
        
        # Token still valid, return current
        credential = TokenManager.get_credential(user_id, service)
        return credential.access_token if hasattr(credential, 'access_token') else None
