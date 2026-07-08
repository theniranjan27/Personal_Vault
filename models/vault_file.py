from app import db
from datetime import datetime

class VaultFile(db.Model):
    """Vault file model for storing encrypted files"""
    
    __tablename__ = 'vault_files'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    encrypted_data = db.Column(db.LargeBinary, nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    is_favorite = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<VaultFile {self.filename}>'
    
    def update_last_accessed(self):
        """Update last accessed timestamp"""
        self.last_accessed = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'filename': self.filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'original_filename': self.original_filename,
            'is_favorite': self.is_favorite,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None
        }