import pytest
from services.encryption import EncryptionService
import base64

@pytest.fixture
def encryption_service():
    return EncryptionService()

def test_encryption_decryption(encryption_service):
    original_text = "Sensitive data: Aadhaar 123456789012"
    encrypted = encryption_service.encrypt(original_text)
    decrypted = encryption_service.decrypt(encrypted)
    assert decrypted == original_text

def test_encryption_empty_string(encryption_service):
    assert encryption_service.encrypt('') == ''
    assert encryption_service.decrypt('') == ''

def test_encryption_binary_data(encryption_service):
    original_bytes = b"Binary file content"
    encrypted = encryption_service.encrypt_bytes(original_bytes)
    decrypted = encryption_service.decrypt_bytes(encrypted)
    assert decrypted == original_bytes

def test_encryption_differs_for_same_input(encryption_service):
    text = "Same text"
    encrypted1 = encryption_service.encrypt(text)
    encrypted2 = encryption_service.encrypt(text)
    assert encrypted1 != encrypted2

def test_decryption_invalid_data(encryption_service):
    invalid_data = "invalid_encrypted_data"
    result = encryption_service.decrypt(invalid_data)
    assert result == ''

def test_encryption_length(encryption_service):
    text = "a" * 1000
    encrypted = encryption_service.encrypt(text)
    assert len(encrypted) > 0
    assert isinstance(encrypted, str)