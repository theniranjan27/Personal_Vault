import re
from typing import Tuple, Optional, Dict, Any

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

# Add other validation functions...

class ValidatorService:
    """Input validation service"""
    
    def validate_password(self, password: str) -> Tuple[bool, Optional[str]]:
        return validate_password(password)
    
    def validate_pin(self, pin: str) -> Tuple[bool, Optional[str]]:
        return validate_pin(pin)
    
    def validate_email(self, email: str) -> Tuple[bool, Optional[str]]:
        return validate_email(email)
    
    def sanitize_input(self, input_string: str, max_length: int = 500) -> str:
        if not input_string:
            return ""
        sanitized = re.sub(r'[<>]', '', input_string)
        return sanitized[:max_length].strip()

# Singleton instance
validator_service = ValidatorService()