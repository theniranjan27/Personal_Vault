from app import db
from datetime import datetime

class VaultCategory(db.Model):
    """Vault categories configuration"""
    
    __tablename__ = 'vault_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    icon = db.Column(db.String(50))
    description = db.Column(db.String(255))
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<VaultCategory {self.name}>'
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'description': self.description,
            'is_default': self.is_default,
            'is_active': self.is_active,
            'sort_order': self.sort_order
        }