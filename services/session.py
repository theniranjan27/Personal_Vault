import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask import session, request, jsonify
from models.user import User
from models.trusted_device import TrustedDevice
from app import db
import jwt

class SessionService:
    """Session management service"""
    
    def __init__(self):
        self.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
        self.timeout_minutes = int(os.environ.get('SESSION_TIMEOUT_MINUTES', 15))
        
    def create_session(self, user_id: int, request_data: Optional[Dict] = None) -> dict:
        """Create a new session for user"""
        session_id = str(uuid.uuid4())
        
        # Get device info
        user_agent = request.headers.get('User-Agent', 'Unknown')
        ip_address = request.remote_addr
        
        # Create session token
        token = jwt.encode({
            'user_id': user_id,
            'session_id': session_id,
            'exp': datetime.utcnow() + timedelta(minutes=self.timeout_minutes)
        }, self.secret_key, algorithm='HS256')
        
        # Store session data
        session['user_id'] = user_id
        session['session_id'] = session_id
        session['login_time'] = datetime.utcnow().isoformat()
        session['token'] = token
        
        # Register device
        self._register_device(user_id, user_agent, ip_address)
        
        return {
            'session_id': session_id,
            'token': token,
            'user_id': user_id,
            'expires_at': datetime.utcnow() + timedelta(minutes=self.timeout_minutes)
        }
        
    def validate_session(self) -> Optional[int]:
        """Validate current session and return user_id if valid"""
        if 'user_id' not in session or 'login_time' not in session:
            return None
            
        # Check timeout
        login_time = datetime.fromisoformat(session['login_time'])
        if datetime.utcnow() - login_time > timedelta(minutes=self.timeout_minutes):
            self.clear_session()
            return None
            
        # Validate token if present
        if 'token' in session:
            try:
                decoded = jwt.decode(session['token'], self.secret_key, algorithms=['HS256'])
                if decoded['user_id'] != session['user_id']:
                    return None
            except jwt.ExpiredSignatureError:
                self.clear_session()
                return None
            except jwt.InvalidTokenError:
                return None
                
        return session['user_id']
        
    def refresh_session(self) -> bool:
        """Refresh session timeout"""
        if 'user_id' not in session:
            return False
            
        session['login_time'] = datetime.utcnow().isoformat()
        
        # Refresh token if exists
        if 'token' in session:
            try:
                decoded = jwt.decode(session['token'], self.secret_key, algorithms=['HS256'])
                new_token = jwt.encode({
                    'user_id': decoded['user_id'],
                    'session_id': decoded['session_id'],
                    'exp': datetime.utcnow() + timedelta(minutes=self.timeout_minutes)
                }, self.secret_key, algorithm='HS256')
                session['token'] = new_token
            except:
                pass
                
        return True
        
    def clear_session(self) -> None:
        """Clear session data"""
        session.clear()
        
    def _register_device(self, user_id: int, user_agent: str, ip_address: str) -> None:
        """Register or update trusted device"""
        device = TrustedDevice.query.filter_by(
            user_id=user_id,
            user_agent=user_agent
        ).first()
        
        if device:
            device.last_used = datetime.utcnow()
            device.ip_address = ip_address
        else:
            device = TrustedDevice(
                user_id=user_id,
                device_name=self._get_device_name(user_agent),
                user_agent=user_agent,
                ip_address=ip_address,
                first_seen=datetime.utcnow(),
                last_used=datetime.utcnow(),
                is_trusted=True
            )
            db.session.add(device)
            
        db.session.commit()
        
    def _get_device_name(self, user_agent: str) -> str:
        """Extract device name from user agent"""
        if 'Chrome' in user_agent:
            return 'Chrome Browser'
        elif 'Firefox' in user_agent:
            return 'Firefox Browser'
        elif 'Safari' in user_agent:
            return 'Safari Browser'
        elif 'Edge' in user_agent:
            return 'Edge Browser'
        elif 'Android' in user_agent:
            return 'Android Device'
        elif 'iPhone' in user_agent or 'iPad' in user_agent:
            return 'iOS Device'
        else:
            return 'Unknown Device'
            
    def get_session_info(self) -> dict:
        """Get current session information"""
        return {
            'user_id': session.get('user_id'),
            'session_id': session.get('session_id'),
            'login_time': session.get('login_time'),
            'timeout_minutes': self.timeout_minutes,
            'is_valid': self.validate_session() is not None
        }
        
    def get_trusted_devices(self, user_id: int) -> list:
        """Get trusted devices for user"""
        devices = TrustedDevice.query.filter_by(user_id=user_id).all()
        return [{
            'id': device.id,
            'name': device.device_name,
            'user_agent': device.user_agent,
            'ip_address': device.ip_address,
            'first_seen': device.first_seen,
            'last_used': device.last_used,
            'is_trusted': device.is_trusted
        } for device in devices]

# Singleton instance
session_service = SessionService()
