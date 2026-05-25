import pytest
from backend.database import db
from backend.database.models import User, Credential
from backend.auth.token_manager import TokenManager
from backend.auth.encryption import encryptor
from datetime import datetime, timedelta


class TestTokenManager:
    """Test token management functionality"""
    
    def test_save_credential(self, app):
        with app.app_context():
            user = User(id='test_user', username='testuser')
            db.session.add(user)
            db.session.commit()
            
            TokenManager.save_credential(
                user_id='test_user',
                service='spotify',
                refresh_token='refresh_token_123',
                access_token_expiry=datetime.utcnow() + timedelta(hours=1)
            )
            
            cred = Credential.query.filter_by(
                user_id='test_user',
                service='spotify'
            ).first()
            
            assert cred is not None
            assert encryptor.decrypt(cred.refresh_token_encrypted) == 'refresh_token_123'
    
    def test_get_credential(self, app):
        with app.app_context():
            user = User(id='test_user', username='testuser')
            db.session.add(user)
            db.session.commit()
            
            TokenManager.save_credential(
                user_id='test_user',
                service='spotify',
                refresh_token='refresh_token_123'
            )
            
            cred = TokenManager.get_credential('test_user', 'spotify')
            assert cred is not None
            assert cred.service == 'spotify'
    
    def test_get_nonexistent_credential(self, app):
        with app.app_context():
            cred = TokenManager.get_credential('test_user', 'spotify')
            assert cred is None
    
    def test_get_refresh_token(self, app):
        with app.app_context():
            user = User(id='test_user', username='testuser')
            db.session.add(user)
            db.session.commit()
            
            TokenManager.save_credential(
                user_id='test_user',
                service='spotify',
                refresh_token='my_secret_token'
            )
            
            token = TokenManager.get_refresh_token('test_user', 'spotify')
            assert token == 'my_secret_token'
    
    def test_update_existing_credential(self, app):
        with app.app_context():
            user = User(id='test_user', username='testuser')
            db.session.add(user)
            db.session.commit()
            
            TokenManager.save_credential(
                user_id='test_user',
                service='spotify',
                refresh_token='token1'
            )
            
            TokenManager.save_credential(
                user_id='test_user',
                service='spotify',
                refresh_token='token2'
            )
            
            token = TokenManager.get_refresh_token('test_user', 'spotify')
            assert token == 'token2'
    
    def test_is_token_valid_with_future_expiry(self, app):
        with app.app_context():
            user = User(id='test_user', username='testuser')
            db.session.add(user)
            db.session.commit()
            
            TokenManager.save_credential(
                user_id='test_user',
                service='spotify',
                refresh_token='token',
                access_token_expiry=datetime.utcnow() + timedelta(hours=1)
            )
            
            assert TokenManager.is_token_valid('test_user', 'spotify') == True
    
    def test_is_token_valid_with_past_expiry(self, app):
        with app.app_context():
            user = User(id='test_user', username='testuser')
            db.session.add(user)
            db.session.commit()
            
            TokenManager.save_credential(
                user_id='test_user',
                service='spotify',
                refresh_token='token',
                access_token_expiry=datetime.utcnow() - timedelta(hours=1)
            )
            
            assert TokenManager.is_token_valid('test_user', 'spotify') == False
    
    def test_is_token_valid_no_credential(self, app):
        with app.app_context():
            assert TokenManager.is_token_valid('test_user', 'spotify') == False
