from app import db
from datetime import datetime

class LoginAttempt(db.Model):
    """Login attempt model for rate limiting"""
    
    __tablename__ = 'login_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    ip_address = db.Column(db.String(45), nullable=False)
    endpoint = db.Column(db.String(100), nullable=False)
    success = db.Column(db.Boolean, default=False)
    attempt_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<LoginAttempt {self.ip_address} at {self.attempt_time}>'
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'endpoint': self.endpoint,
            'success': self.success,
            'attempt_time': self.attempt_time.isoformat() if self.attempt_time else None
        }