from app import db
from datetime import datetime

class Note(db.Model):
    """Note model for storing encrypted notes"""
    
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=True)
    tags = db.Column(db.String(255), nullable=True)  # Comma separated tags
    is_favorite = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Note {self.title}>'
    
    def get_tags(self) -> list:
        """Get tags as list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def set_tags(self, tags: list):
        """Set tags from list"""
        self.tags = ', '.join(tags) if tags else None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'tags': self.get_tags(),
            'is_favorite': self.is_favorite,
            'is_archived': self.is_archived,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }