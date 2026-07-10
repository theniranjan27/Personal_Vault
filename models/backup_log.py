from app import db
from datetime import datetime

class BackupLog(db.Model):
    """Backup log model for tracking backups"""
    
    __tablename__ = 'backup_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    items_count = db.Column(db.Integer, default=0)
    checksum = db.Column(db.String(64), nullable=True)  # SHA-256 checksum
    status = db.Column(db.String(30), default='Not Verified')  # Verified, Not Verified, Failed, Corrupted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_verified_at = db.Column(db.DateTime, nullable=True)
    download_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<BackupLog {self.file_name}>'
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'file_name': self.file_name,
            'backup_id': self.file_name,  # backward-compatible backup_id alias
            'filename': self.file_name,   # backward-compatible filename alias
            'file_path': self.file_path,
            'file_size': self.file_size,
            'size': self.file_size,       # backward-compatible size alias
            'items_count': self.items_count,
            'items': self.items_count,     # backward-compatible items alias
            'checksum': self.checksum,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_verified_at': self.last_verified_at.isoformat() if self.last_verified_at else None,
            'restored_at': self.last_verified_at.isoformat() if self.last_verified_at else None,  # backward-compatible restored_at alias
            'download_count': self.download_count
        }