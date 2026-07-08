from app import db
from datetime import datetime
import json

class SecurityMethod(db.Model):
    """Security methods configuration"""
    
    __tablename__ = 'security_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # password, pin, otp, totp, webauthn, hardware
    enabled = db.Column(db.Boolean, default=False)
    required = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(255))
    icon = db.Column(db.String(50))
    config = db.Column(db.Text, nullable=True)  # JSON config
    status = db.Column(db.String(20), default='active')  # active, coming, disabled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SecurityMethod {self.name}>'
    
    def get_config(self) -> dict:
        """Get config as dictionary"""
        if self.config:
            return json.loads(self.config)
        return {}
    
    def set_config(self, config: dict):
        """Set config from dictionary"""
        self.config = json.dumps(config)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'enabled': self.enabled,
            'required': self.required,
            'description': self.description,
            'icon': self.icon,
            'config': self.get_config(),
            'status': self.status
        }