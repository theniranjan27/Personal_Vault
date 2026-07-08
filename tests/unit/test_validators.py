import pytest
from utils.validators import (
    validate_password, validate_pin, validate_email,
    validate_username, validate_url, validate_phone,
    validate_aadhaar, validate_pan, validate_passport,
    validate_ifsc, validate_upi, sanitize_input
)

def test_validate_password_valid():
    valid, msg = validate_password("SecurePass123!")
    assert valid
    assert msg is None

def test_validate_password_too_short():
    valid, msg = validate_password("Short1!")
    assert not valid
    assert "at least 8 characters" in msg

def test_validate_password_no_uppercase():
    valid, msg = validate_password("securepass123!")
    assert not valid
    assert "uppercase" in msg

def test_validate_password_no_lowercase():
    valid, msg = validate_password("SECUREPASS123!")
    assert not valid
    assert "lowercase" in msg

def test_validate_password_no_number():
    valid, msg = validate_password("SecurePass!")
    assert not valid
    assert "number" in msg

def test_validate_password_no_special():
    valid, msg = validate_password("SecurePass123")
    assert not valid
    assert "special" in msg

def test_validate_pin_valid():
    valid, msg = validate_pin("123456")
    assert valid
    assert msg is None

def test_validate_pin_too_short():
    valid, msg = validate_pin("12345")
    assert not valid
    assert "exactly 6 digits" in msg

def test_validate_pin_too_long():
    valid, msg = validate_pin("1234567")
    assert not valid
    assert "exactly 6 digits" in msg

def test_validate_pin_non_digit():
    valid, msg = validate_pin("12345a")
    assert not valid
    assert "only numbers" in msg

def test_validate_email_valid():
    valid, msg = validate_email("user@example.com")
    assert valid
    assert msg is None

def test_validate_email_invalid():
    valid, msg = validate_email("invalid-email")
    assert not valid
    assert "Invalid email" in msg

def test_validate_username_valid():
    valid, msg = validate_username("test_user")
    assert valid
    assert msg is None

def test_validate_username_invalid_chars():
    valid, msg = validate_username("test@user")
    assert not valid
    assert "only contain letters" in msg

def test_validate_username_too_short():
    valid, msg = validate_username("ab")
    assert not valid
    assert "at least 3 characters" in msg

def test_validate_url_valid():
    valid, msg = validate_url("https://example.com")
    assert valid
    assert msg is None

def test_validate_url_invalid():
    valid, msg = validate_url("not-a-url")
    assert not valid
    assert "Invalid URL" in msg

def test_validate_phone_valid():
    valid, msg = validate_phone("+1234567890")
    assert valid
    assert msg is None

def test_validate_aadhaar_valid():
    valid, msg = validate_aadhaar("123456789012")
    assert valid
    assert msg is None

def test_validate_aadhaar_invalid_length():
    valid, msg = validate_aadhaar("1234567890")
    assert not valid
    assert "12 digits" in msg

def test_validate_pan_valid():
    valid, msg = validate_pan("ABCDE1234F")
    assert valid
    assert msg is None

def test_validate_pan_invalid():
    valid, msg = validate_pan("ABCD1234E")
    assert not valid
    assert "Invalid PAN" in msg

def test_validate_passport_valid():
    valid, msg = validate_passport("P1234567")
    assert valid
    assert msg is None

def test_validate_ifsc_valid():
    valid, msg = validate_ifsc("SBIN0001234")
    assert valid
    assert msg is None

def test_validate_ifsc_invalid():
    valid, msg = validate_ifsc("SBIN123456")
    assert not valid
    assert "Invalid IFSC" in msg

def test_validate_upi_valid():
    valid, msg = validate_upi("user@paytm")
    assert valid
    assert msg is None

def test_sanitize_input():
    input_str = "  <script>alert('xss')</script>  Hello World  "
    sanitized = sanitize_input(input_str)
    assert "<script>" not in sanitized
    assert "Hello World" in sanitized
    assert sanitized.startswith("Hello") or sanitized == "Hello World"