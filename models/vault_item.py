from app import db
from datetime import datetime
import json

class VaultItem(db.Model):
    """Vault item model for storing encrypted data"""
    
    __tablename__ = 'vault_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    label = db.Column(db.String(100), nullable=False)
    encrypted_value = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    extra = db.Column(db.Text, nullable=True)  # JSON extra fields
    is_favorite = db.Column(db.Boolean, default=False)
    is_sensitive = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<VaultItem {self.category}: {self.label}>'
    
    def get_extra(self) -> dict:
        """Get extra fields as dictionary"""
        if self.extra:
            return json.loads(self.extra)
        return {}
    
    def set_extra(self, extra: dict):
        """Set extra fields from dictionary"""
        self.extra = json.dumps(extra) if extra else None
    
    def update_last_accessed(self):
        """Update last accessed timestamp"""
        self.last_accessed = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'category': self.category,
            'label': self.label,
            'notes': self.notes,
            'extra': self.get_extra(),
            'is_favorite': self.is_favorite,
            'is_sensitive': self.is_sensitive,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None
        }