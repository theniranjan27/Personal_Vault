import re
from typing import Tuple, Optional

def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None

def validate_pin(pin: str) -> Tuple[bool, Optional[str]]:
    if not pin:
        return False, "PIN is required"
    
    if len(pin) != 6:
        return False, "PIN must be exactly 6 digits"
    
    if not pin.isdigit():
        return False, "PIN must contain only numbers"
    
    return True, None

def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    if not email:
        return False, "Email is required"
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, None

def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    if not username:
        return False, "Username is required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 50:
        return False, "Username must be less than 50 characters"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, None

def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    if not url:
        return True, None
    
    pattern = r'^https?://[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)+([/?].*)?$'
    if not re.match(pattern, url):
        return False, "Invalid URL format"
    
    return True, None

def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    if not phone:
        return True, None
    
    pattern = r'^\+?[0-9]{10,15}$'
    if not re.match(pattern, phone):
        return False, "Invalid phone number format"
    
    return True, None

def validate_aadhaar(aadhaar: str) -> Tuple[bool, Optional[str]]:
    if not aadhaar:
        return True, None
    
    cleaned = re.sub(r'[^0-9]', '', aadhaar)
    if len(cleaned) != 12:
        return False, "Aadhaar must be 12 digits"
    
    if not cleaned.isdigit():
        return False, "Aadhaar must contain only digits"
    
    return True, None

def validate_pan(pan: str) -> Tuple[bool, Optional[str]]:
    if not pan:
        return True, None
    
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    if not re.match(pattern, pan):
        return False, "Invalid PAN format (should be ABCDE1234F)"
    
    return True, None

def validate_passport(passport: str) -> Tuple[bool, Optional[str]]:
    if not passport:
        return True, None
    
    pattern = r'^[A-Z0-9]{6,9}$'
    if not re.match(pattern, passport):
        return False, "Invalid passport format"
    
    return True, None

def validate_ifsc(ifsc: str) -> Tuple[bool, Optional[str]]:
    if not ifsc:
        return True, None
    
    pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
    if not re.match(pattern, ifsc):
        return False, "Invalid IFSC code format"
    
    return True, None

def validate_upi(upi: str) -> Tuple[bool, Optional[str]]:
    if not upi:
        return True, None
    
    pattern = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9]+$'
    if not re.match(pattern, upi):
        return False, "Invalid UPI ID format"
    
    return True, None

def sanitize_input(input_string: str, max_length: int = 500) -> str:
    if not input_string:
        return ""
    
    # Remove script tags and their contents
    sanitized = re.sub(r'<script\b[^>]*>([\s\S]*?)<\/script>', '', input_string, flags=re.IGNORECASE)
    # Remove HTML tags
    sanitized = re.sub(r'<[^>]*>', '', sanitized)
    sanitized = sanitized[:max_length]
    return sanitized.strip()