from app import db
from datetime import datetime

class BackupLog(db.Model):
    """Backup log model for tracking backups"""
    
    __tablename__ = 'backup_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    backup_id = db.Column(db.String(100), nullable=False, unique=True)
    filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    items_count = db.Column(db.Integer, default=0)
    files_count = db.Column(db.Integer, default=0)
    restored_items = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='success')  # success, failed, in-progress
    encrypted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    restored_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<BackupLog {self.backup_id}>'
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'backup_id': self.backup_id,
            'filename': self.filename,
            'file_size': self.file_size,
            'items_count': self.items_count,
            'files_count': self.files_count,
            'restored_items': self.restored_items,
            'status': self.status,
            'encrypted': self.encrypted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'restored_at': self.restored_at.isoformat() if self.restored_at else None
        }