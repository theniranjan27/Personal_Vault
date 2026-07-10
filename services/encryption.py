import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from typing import Optional, Union, Any
import json

class EncryptionService:
    """AES-256 encryption service using Fernet"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        if encryption_key:
            self.key = encryption_key
        else:
            self.key = os.environ.get('ENCRYPTION_KEY')
            
        if not self.key:
            # Generate a key for development
            self.key = base64.urlsafe_b64encode(os.urandom(32)).decode()
            
        self.cipher = Fernet(self.key.encode() if isinstance(self.key, str) else self.key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        if not data:
            return ''
        
        try:
            encrypted = self.cipher.encrypt(data.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        if not encrypted_data:
            return ''
        
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode('utf-8')
        except Exception as e:
            return ''
    
    def encrypt_bytes(self, data: bytes) -> bytes:
        """Encrypt binary data"""
        if not data:
            return b''
        
        try:
            return self.cipher.encrypt(data)
        except Exception as e:
            raise ValueError(f"Binary encryption failed: {str(e)}")
    
    def decrypt_bytes(self, encrypted_data: bytes) -> bytes:
        """Decrypt binary data"""
        if not encrypted_data:
            return b''
        
        try:
            return self.cipher.decrypt(encrypted_data)
        except Exception as e:
            raise ValueError(f"Binary decryption failed: {str(e)}")
    
    def encrypt_json(self, data: Any) -> str:
        """Encrypt JSON data"""
        json_str = json.dumps(data)
        return self.encrypt(json_str)
    
    def decrypt_json(self, encrypted_data: str) -> Any:
        """Decrypt JSON data"""
        json_str = self.decrypt(encrypted_data)
        return json.loads(json_str)
    
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """Encrypt a file"""
        with open(file_path, 'rb') as f:
            data = f.read()
        
        encrypted = self.encrypt_bytes(data)
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(encrypted)
            return output_path
        
        return encrypted
    
    def decrypt_file(self, encrypted_path: str, output_path: Optional[str] = None) -> str:
        """Decrypt a file"""
        with open(encrypted_path, 'rb') as f:
            encrypted = f.read()
        
        decrypted = self.decrypt_bytes(encrypted)
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(decrypted)
            return output_path
        
        return decrypted

# Singleton instance
encryption_service = EncryptionService()
