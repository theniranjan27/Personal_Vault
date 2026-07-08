from app import db
from datetime import datetime

class VaultField(db.Model):
    """Custom fields for vault items"""
    
    __tablename__ = 'vault_fields'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    field_name = db.Column(db.String(100), nullable=False)
    field_type = db.Column(db.String(50), default='text')  # text, number, date, boolean
    is_required = db.Column(db.Boolean, default=False)
    is_sensitive = db.Column(db.Boolean, default=False)
    default_value = db.Column(db.String(255), nullable=True)
    options = db.Column(db.Text, nullable=True)  # JSON options for select fields
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<VaultField {self.category}: {self.field_name}>'
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'field_name': self.field_name,
            'field_type': self.field_type,
            'is_required': self.is_required,
            'is_sensitive': self.is_sensitive,
            'default_value': self.default_value,
            'options': self.options,
            'sort_order': self.sort_order
        }