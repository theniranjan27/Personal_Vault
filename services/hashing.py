import bcrypt
import argon2
from argon2 import PasswordHasher
from typing import Tuple, Optional
import os

class PasswordService:
    """Password hashing service using Argon2 and bcrypt"""
    
    def __init__(self):
        self.ph = PasswordHasher()
        self.argon2_available = True
        self.bcrypt_rounds = int(os.environ.get('BCRYPT_ROUNDS', 12))
    
    def hash_password(self, password: str) -> str:
        """Hash password using Argon2 (preferred)"""
        if not password:
            raise ValueError("Password cannot be empty")
        
        try:
            return self.ph.hash(password)
        except Exception as e:
            raise ValueError(f"Password hashing failed: {str(e)}")
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against Argon2 hash"""
        if not password or not hashed:
            return False
        
        try:
            return self.ph.verify(hashed, password)
        except argon2.exceptions.VerificationError:
            return False
        except Exception:
            return False
    
    def hash_pin(self, pin: str) -> str:
        """Hash PIN using bcrypt (faster for short strings)"""
        if not pin:
            raise ValueError("PIN cannot be empty")
        
        if not pin.isdigit():
            raise ValueError("PIN must contain only digits")
        
        if len(pin) != 6:
            raise ValueError("PIN must be exactly 6 digits")
        
        try:
            salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)
            return bcrypt.hashpw(pin.encode('utf-8'), salt).decode('utf-8')
        except Exception as e:
            raise ValueError(f"PIN hashing failed: {str(e)}")
    
    def verify_pin(self, pin: str, hashed: str) -> bool:
        """Verify PIN against bcrypt hash"""
        if not pin or not hashed:
            return False
        
        try:
            return bcrypt.checkpw(pin.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    
    def hash_string(self, value: str, salt: Optional[str] = None) -> str:
        """Generic string hashing using SHA-256"""
        import hashlib
        
        if not value:
            return ''
        
        if salt:
            value = salt + value
        
        return hashlib.sha256(value.encode('utf-8')).hexdigest()
    
    def check_password_strength(self, password: str) -> dict:
        """Check password strength and return score"""
        score = 0
        feedback = []
        
        if len(password) < 8:
            feedback.append("Password must be at least 8 characters long")
        else:
            score += 1
        
        if any(c.islower() for c in password):
            score += 1
        else:
            feedback.append("Password must contain at least one lowercase letter")
            
        if any(c.isupper() for c in password):
            score += 1
        else:
            feedback.append("Password must contain at least one uppercase letter")
            
        if any(c.isdigit() for c in password):
            score += 1
        else:
            feedback.append("Password must contain at least one digit")
            
        if any(c in '!@#$%^&*(),.?":{}|<>' for c in password):
            score += 1
        else:
            feedback.append("Password must contain at least one special character")
            
        if score <= 2:
            strength = 'weak'
            color = '#ef5350' # Red
        elif score <= 4:
            strength = 'medium'
            color = '#ffca28' # Yellow
        else:
            strength = 'strong'
            color = '#66bb6a' # Green
            
        return {
            'score': score,
            'max_score': 5,
            'strength': strength,
            'color': color,
            'feedback': feedback
        }

# Singleton instance
password_service = PasswordService()
