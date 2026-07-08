from app import db
from datetime import datetime

class TrustedDevice(db.Model):
    """Trusted device model for device management"""
    
    __tablename__ = 'trusted_devices'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    device_name = db.Column(db.String(100), nullable=False)
    user_agent = db.Column(db.String(255), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    is_trusted = db.Column(db.Boolean, default=True)
    is_current = db.Column(db.Boolean, default=False)
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TrustedDevice {self.device_name}>'
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'device_name': self.device_name,
            'user_agent': self.user_agent,
            'ip_address': self.ip_address,
            'is_trusted': self.is_trusted,
            'is_current': self.is_current,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_used': self.last_used.isoformat() if self.last_used else None
        }