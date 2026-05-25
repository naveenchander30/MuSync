from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from backend.config import MASTER_PASSWORD

class TokenEncryptor:
    """Encrypt and decrypt OAuth tokens"""
    
    def __init__(self, master_password: str = None):
        password = master_password or MASTER_PASSWORD
        salt = b'musync_salt_2024'
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.fernet = Fernet(key)
    
    def encrypt(self, token: str) -> str:
        """Encrypt a token string"""
        encrypted = self.fernet.encrypt(token.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_token: str) -> str:
        """Decrypt a token string"""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_token)
        return self.fernet.decrypt(encrypted_bytes).decode()

encryptor = TokenEncryptor()
