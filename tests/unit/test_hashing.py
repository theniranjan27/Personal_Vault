import pytest
from services.hashing import PasswordService

@pytest.fixture
def password_service():
    return PasswordService()

def test_password_hashing(password_service):
    password = "SecurePass123!"
    hashed = password_service.hash_password(password)
    assert hashed != password
    assert password_service.verify_password(password, hashed)

def test_password_verification_wrong(password_service):
    password = "SecurePass123!"
    hashed = password_service.hash_password(password)
    assert not password_service.verify_password("WrongPassword", hashed)

def test_pin_hashing(password_service):
    pin = "123456"
    hashed = password_service.hash_pin(pin)
    assert hashed != pin
    assert password_service.verify_pin(pin, hashed)

def test_pin_verification_wrong(password_service):
    pin = "123456"
    hashed = password_service.hash_pin(pin)
    assert not password_service.verify_pin("654321", hashed)

def test_argon2_consistency(password_service):
    password = "TestPassword123!"
    hashed1 = password_service.hash_password(password)
    hashed2 = password_service.hash_password(password)
    assert hashed1 != hashed2
    assert password_service.verify_password(password, hashed1)
    assert password_service.verify_password(password, hashed2)

def test_bcrypt_consistency(password_service):
    pin = "123456"
    hashed1 = password_service.hash_pin(pin)
    hashed2 = password_service.hash_pin(pin)
    assert hashed1 != hashed2
    assert password_service.verify_pin(pin, hashed1)
    assert password_service.verify_pin(pin, hashed2)