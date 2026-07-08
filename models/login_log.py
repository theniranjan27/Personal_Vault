from app import db
from datetime import datetime

class LoginLog(db.Model):
    """Login log model for tracking user logins/logouts"""
    
    __tablename__ = 'login_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.String(255), nullable=True)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    logout_time = db.Column(db.DateTime, nullable=True)
    login_success = db.Column(db.Boolean, default=False)
    failure_reason = db.Column(db.String(255), nullable=True)
    
    def __repr__(self):
        return f'<LoginLog user_id={self.user_id} success={self.login_success} at {self.login_time}>'
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'login_time': self.login_time.isoformat() if self.login_time else None,
            'logout_time': self.logout_time.isoformat() if self.logout_time else None,
            'login_success': self.login_success,
            'failure_reason': self.failure_reason
        }
