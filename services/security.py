from models.user import User
from models.security_method import SecurityMethod
from models.security_setting import SecuritySetting
from app import db
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import os
import hashlib

class SecurityService:
    """Security management service"""
    
    def __init__(self):
        self.max_attempts = int(os.environ.get('MAX_LOGIN_ATTEMPTS', 5))
        self.lockout_minutes = int(os.environ.get('LOCKOUT_DURATION_MINUTES', 30))
    
    def get_security_methods(self, user_id: int) -> List[dict]:
        """Get all security methods for user"""
        methods = SecurityMethod.query.filter_by(user_id=user_id).all()
        
        if not methods:
            # Create default methods
            methods = self._create_default_methods(user_id)
        
        return [{
            'id': method.id,
            'name': method.name,
            'type': method.type,
            'enabled': method.enabled,
            'required': method.required,
            'description': method.description,
            'icon': method.icon,
            'config': method.config,
            'status': method.status
        } for method in methods]
    
    def _create_default_methods(self, user_id: int) -> List[SecurityMethod]:
        """Create default security methods for user"""
        default_methods = [
            {
                'name': 'Master Password',
                'type': 'password',
                'enabled': True,
                'required': True,
                'description': 'Strong password with letters, numbers, and symbols',
                'icon': '🔑',
                'config': {'min_length': 8, 'require_special': True},
                'status': 'active'
            },
            {
                'name': 'PIN Verification',
                'type': 'pin',
                'enabled': True,
                'required': True,
                'description': '6-digit PIN for second authentication layer',
                'icon': '🔢',
                'config': {'length': 6},
                'status': 'active'
            },
            {
                'name': 'Email OTP',
                'type': 'otp',
                'enabled': False,
                'required': False,
                'description': 'One-time password sent to registered email',
                'icon': '✉️',
                'config': {'length': 6, 'expiry': 300},
                'status': 'coming'
            },
            {
                'name': 'Authenticator App OTP',
                'type': 'totp',
                'enabled': False,
                'required': False,
                'description': 'TOTP from Google Authenticator or similar',
                'icon': '📱',
                'config': {'issuer': 'Private Vault', 'period': 30},
                'status': 'coming'
            }
        ]
        
        import json
        methods = []
        for method_data in default_methods:
            if 'config' in method_data and isinstance(method_data['config'], dict):
                method_data['config'] = json.dumps(method_data['config'])
            method = SecurityMethod(
                user_id=user_id,
                **method_data
            )
            db.session.add(method)
            methods.append(method)
        
        db.session.commit()
        return methods
    
    def toggle_security_method(self, user_id: int, method_id: int, enabled: bool) -> bool:
        """Enable or disable a security method"""
        method = SecurityMethod.query.filter_by(
            user_id=user_id,
            id=method_id
        ).first()
        
        if not method or method.required:
            return False
        
        method.enabled = enabled
        db.session.commit()
        return True
    
    def get_security_settings(self, user_id: int) -> dict:
        """Get security settings for user"""
        setting = SecuritySetting.query.filter_by(user_id=user_id).first()
        
        if not setting:
            setting = SecuritySetting(
                user_id=user_id,
                session_timeout_minutes=int(os.environ.get('SESSION_TIMEOUT_MINUTES', 15)),
                max_login_attempts=int(os.environ.get('MAX_LOGIN_ATTEMPTS', 5)),
                lockout_duration_minutes=int(os.environ.get('LOCKOUT_DURATION_MINUTES', 30)),
                two_factor_enabled=False
            )
            db.session.add(setting)
            db.session.commit()
        
        return {
            'session_timeout_minutes': setting.session_timeout_minutes,
            'max_login_attempts': setting.max_login_attempts,
            'lockout_duration_minutes': setting.lockout_duration_minutes,
            'two_factor_enabled': setting.two_factor_enabled,
            'last_modified': setting.last_modified
        }
    
    def update_security_settings(self, user_id: int, settings: dict) -> bool:
        """Update security settings"""
        setting = SecuritySetting.query.filter_by(user_id=user_id).first()
        
        if not setting:
            setting = SecuritySetting(user_id=user_id)
            db.session.add(setting)
        
        if 'session_timeout_minutes' in settings:
            setting.session_timeout_minutes = settings['session_timeout_minutes']
        
        if 'max_login_attempts' in settings:
            setting.max_login_attempts = settings['max_login_attempts']
        
        if 'lockout_duration_minutes' in settings:
            setting.lockout_duration_minutes = settings['lockout_duration_minutes']
        
        if 'two_factor_enabled' in settings:
            setting.two_factor_enabled = settings['two_factor_enabled']
        
        setting.last_modified = datetime.utcnow()
        db.session.commit()
        return True
    
    def check_login_attempts(self, user: User) -> bool:
        """Check if user is locked out"""
        if user.locked_until and user.locked_until > datetime.utcnow():
            return False
        
        return True
    
    def handle_failed_attempt(self, user: User) -> dict:
        """Handle a failed login attempt"""
        user.failed_attempts += 1
        locked = False
        
        if user.failed_attempts > self.max_attempts:
            user.locked_until = datetime.utcnow() + timedelta(minutes=self.lockout_minutes)
            locked = True
        
        db.session.commit()
        
        return {
            'locked': locked,
            'remaining': self.max_attempts - user.failed_attempts if not locked else 0,
            'lockout_minutes': self.lockout_minutes if locked else 0
        }
    
    def reset_attempts(self, user: User) -> None:
        """Reset failed login attempts"""
        user.failed_attempts = 0
        user.locked_until = None
        db.session.commit()
    
    def generate_recovery_codes(self, user_id: int, count: int = 10) -> List[str]:
        """Generate recovery codes for user"""
        import secrets
        
        codes = []
        for _ in range(count):
            code = secrets.token_hex(4).upper()
            codes.append(code)
        
        # Store hashed codes (simplified)
        # In production, store hashed versions
        return codes

# Singleton instance
security_service = SecurityService()