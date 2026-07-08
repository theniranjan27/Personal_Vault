from app import db
from datetime import datetime
from typing import Optional

class User(db.Model):
    """User model for admin/single user"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    master_password_hash = db.Column(db.String(200), nullable=False)
    pin_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    failed_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    avatar = db.Column(db.String(255), nullable=True)
    
    # Relationships - use string references to avoid circular imports
    vault_items = db.relationship('VaultItem', backref='user', lazy=True, cascade='all, delete-orphan')
    vault_files = db.relationship('VaultFile', backref='user', lazy=True, cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='user', lazy=True, cascade='all, delete-orphan')
    activity_logs = db.relationship('ActivityLog', backref='user', lazy=True, cascade='all, delete-orphan')
    backup_logs = db.relationship('BackupLog', backref='user', lazy=True, cascade='all, delete-orphan')
    trusted_devices = db.relationship('TrustedDevice', backref='user', lazy=True, cascade='all, delete-orphan')
    security_methods = db.relationship('SecurityMethod', backref='user', lazy=True, cascade='all, delete-orphan')
    security_settings = db.relationship('SecuritySetting', backref='user', uselist=False, lazy=True, cascade='all, delete-orphan')
    login_logs = db.relationship('LoginLog', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def is_locked(self) -> bool:
        """Check if user account is locked"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def get_remaining_lockout(self) -> Optional[int]:
        """Get remaining lockout time in minutes"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            delta = self.locked_until - datetime.utcnow()
            return int(delta.total_seconds() / 60)
        return None
    
    def to_dict(self) -> dict:
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'avatar': self.avatar
        }