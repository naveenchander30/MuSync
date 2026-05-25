import pytest
from backend.auth.encryption import TokenEncryptor


class TestTokenEncryptor:
    """Test token encryption/decryption"""
    
    def test_encrypt_and_decrypt(self):
        encryptor = TokenEncryptor(master_password='test_password')
        token = 'my_secret_refresh_token'
        
        encrypted = encryptor.encrypt(token)
        decrypted = encryptor.decrypt(encrypted)
        
        assert decrypted == token
    
    def test_different_passwords_fail(self):
        encryptor1 = TokenEncryptor(master_password='password1')
        encryptor2 = TokenEncryptor(master_password='password2')
        
        token = 'secret_token'
        encrypted = encryptor1.encrypt(token)
        
        with pytest.raises(Exception):
            encryptor2.decrypt(encrypted)
    
    def test_encrypted_output_differs_from_input(self):
        encryptor = TokenEncryptor(master_password='test_password')
        token = 'test_token'
        
        encrypted = encryptor.encrypt(token)
        assert encrypted != token
    
    def test_same_token_different_encryptions(self):
        """Each encryption should produce different output (for security)"""
        encryptor = TokenEncryptor(master_password='test_password')
        token = 'test_token'
        
        encrypted1 = encryptor.encrypt(token)
        encrypted2 = encryptor.encrypt(token)
        
        # Should be different due to initialization vector
        assert encrypted1 != encrypted2
    
    def test_decrypt_returns_original(self):
        encryptor = TokenEncryptor(master_password='test_password')
        original = 'refresh_token_12345'
        
        encrypted = encryptor.encrypt(original)
        decrypted = encryptor.decrypt(encrypted)
        
        assert decrypted == original
    
    def test_empty_token(self):
        encryptor = TokenEncryptor(master_password='test_password')
        
        encrypted = encryptor.encrypt('')
        decrypted = encryptor.decrypt(encrypted)
        
        assert decrypted == ''
    
    def test_long_token(self):
        encryptor = TokenEncryptor(master_password='test_password')
        long_token = 'a' * 10000
        
        encrypted = encryptor.encrypt(long_token)
        decrypted = encryptor.decrypt(encrypted)
        
        assert decrypted == long_token
