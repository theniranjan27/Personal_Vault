from app import db
from datetime import datetime

class SecuritySetting(db.Model):
    """Security settings for user"""
    
    __tablename__ = 'security_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    session_timeout_minutes = db.Column(db.Integer, default=15)
    max_login_attempts = db.Column(db.Integer, default=5)
    lockout_duration_minutes = db.Column(db.Integer, default=30)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    ip_restriction_enabled = db.Column(db.Boolean, default=False)
    allowed_ips = db.Column(db.Text, nullable=True)  # Comma separated IPs
    device_alert_enabled = db.Column(db.Boolean, default=False)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SecuritySetting user_id={self.user_id}>'
    
    def get_allowed_ips(self) -> list:
        """Get list of allowed IPs"""
        if self.allowed_ips:
            return [ip.strip() for ip in self.allowed_ips.split(',') if ip.strip()]
        return []
    
    def set_allowed_ips(self, ips: list):
        """Set allowed IPs from list"""
        self.allowed_ips = ', '.join(ips) if ips else None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'session_timeout_minutes': self.session_timeout_minutes,
            'max_login_attempts': self.max_login_attempts,
            'lockout_duration_minutes': self.lockout_duration_minutes,
            'two_factor_enabled': self.two_factor_enabled,
            'ip_restriction_enabled': self.ip_restriction_enabled,
            'allowed_ips': self.get_allowed_ips(),
            'device_alert_enabled': self.device_alert_enabled,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None
        }