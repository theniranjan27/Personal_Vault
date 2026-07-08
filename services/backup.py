import json
import os
import zipfile
from datetime import datetime
from typing import Optional, Dict, Any, List
from app import db
from models.backup_log import BackupLog
from models.vault_item import VaultItem
from models.vault_file import VaultFile
from models.note import Note
from services.encryption import encryption_service
from services.audit import audit_service
from flask import current_app
import tempfile

class BackupService:
    """Backup and restore service"""
    
    def __init__(self):
        self.backup_dir = 'backups'
        self.ensure_backup_dir()
    
    def ensure_backup_dir(self):
        """Ensure backup directory exists"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self, user_id: int, password: Optional[str] = None,
                      include_files: bool = True, include_settings: bool = True) -> dict:
        """Create a backup of user data"""
        timestamp = datetime.utcnow().isoformat()
        backup_id = f"backup_{user_id}_{timestamp.replace(':', '-')}"
        
        # Gather data
        backup_data = {
            'type': 'vault_backup',
            'version': '1.0',
            'timestamp': timestamp,
            'user_id': user_id,
            'items': self._get_items(user_id),
            'files': self._get_file_metadata(user_id) if include_files else [],
            'notes': self._get_notes(user_id),
            'settings': self._get_settings(user_id) if include_settings else {}
        }
        
        # Serialize and encrypt
        json_data = json.dumps(backup_data, default=str)
        
        if password:
            # Use password-based encryption (simplified)
            encrypted_data = encryption_service.encrypt(json_data)
        else:
            encrypted_data = json_data
        
        # Save backup file
        filename = f"{backup_id}.backup"
        filepath = os.path.join(self.backup_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(encrypted_data)
        
        # Log backup
        backup_log = BackupLog(
            user_id=user_id,
            backup_id=backup_id,
            filename=filename,
            file_size=os.path.getsize(filepath),
            created_at=datetime.utcnow(),
            status='success',
            items_count=len(backup_data['items']),
            files_count=len(backup_data['files']),
            encrypted=bool(password)
        )
        db.session.add(backup_log)
        db.session.commit()
        
        # Audit log
        audit_service.log_action(
            user_id=user_id,
            action='backup_created',
            details={
                'backup_id': backup_id,
                'items': len(backup_data['items']),
                'files': len(backup_data['files'])
            }
        )
        
        return {
            'backup_id': backup_id,
            'filename': filename,
            'filepath': filepath,
            'items': len(backup_data['items']),
            'files': len(backup_data['files']),
            'size': os.path.getsize(filepath)
        }
    
    def restore_backup(self, user_id: int, backup_id: str, 
                       password: Optional[str] = None) -> dict:
        """Restore from a backup"""
        # Find backup log
        backup_log = BackupLog.query.filter_by(
            user_id=user_id,
            backup_id=backup_id
        ).first()
        
        if not backup_log:
            raise ValueError("Backup not found")
        
        # Read backup file
        filepath = os.path.join(self.backup_dir, backup_log.filename)
        
        if not os.path.exists(filepath):
            raise ValueError("Backup file not found")
        
        with open(filepath, 'r') as f:
            encrypted_data = f.read()
        
        # Decrypt if needed
        if backup_log.encrypted:
            if not password:
                raise ValueError("Password required for encrypted backup")
            json_data = encryption_service.decrypt(encrypted_data)
        else:
            json_data = encrypted_data
        
        # Parse backup data
        backup_data = json.loads(json_data)
        
        # Validate backup
        if backup_data.get('type') != 'vault_backup':
            raise ValueError("Invalid backup file")
        
        # Restore data
        restored_items = self._restore_items(user_id, backup_data.get('items', []))
        restored_notes = self._restore_notes(user_id, backup_data.get('notes', []))
        
        # Update backup log
        backup_log.restored_at = datetime.utcnow()
        backup_log.restored_items = len(restored_items)
        db.session.commit()
        
        # Audit log
        audit_service.log_action(
            user_id=user_id,
            action='backup_restored',
            details={
                'backup_id': backup_id,
                'items': len(restored_items),
                'notes': len(restored_notes)
            }
        )
        
        return {
            'items': len(restored_items),
            'notes': len(restored_notes)
        }
    
    def get_backup_history(self, user_id: int, limit: int = 50) -> list:
        """Get backup history for user"""
        logs = BackupLog.query.filter_by(user_id=user_id)\
            .order_by(BackupLog.created_at.desc())\
            .limit(limit)\
            .all()
        
        return [{
            'id': log.id,
            'backup_id': log.backup_id,
            'filename': log.filename,
            'created_at': log.created_at,
            'file_size': log.file_size,
            'items_count': log.items_count,
            'files_count': log.files_count,
            'status': log.status,
            'encrypted': log.encrypted,
            'restored_at': log.restored_at
        } for log in logs]
    
    def delete_backup(self, user_id: int, backup_id: str) -> bool:
        """Delete a backup"""
        backup_log = BackupLog.query.filter_by(
            user_id=user_id,
            backup_id=backup_id
        ).first()
        
        if not backup_log:
            return False
        
        # Delete file
        filepath = os.path.join(self.backup_dir, backup_log.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Delete log
        db.session.delete(backup_log)
        db.session.commit()
        
        # Audit log
        audit_service.log_action(
            user_id=user_id,
            action='backup_deleted',
            details={'backup_id': backup_id}
        )
        
        return True
    
    def export_backup(self, user_id: int, backup_id: str) -> bytes:
        """Export backup as downloadable file"""
        backup_log = BackupLog.query.filter_by(
            user_id=user_id,
            backup_id=backup_id
        ).first()
        
        if not backup_log:
            raise ValueError("Backup not found")
        
        filepath = os.path.join(self.backup_dir, backup_log.filename)
        
        with open(filepath, 'rb') as f:
            return f.read()
    
    def _get_items(self, user_id: int) -> list:
        """Get vault items for backup"""
        items = VaultItem.query.filter_by(user_id=user_id).all()
        return [{
            'id': item.id,
            'category': item.category,
            'label': item.label,
            'encrypted_value': item.encrypted_value,
            'notes': item.notes,
            'is_favorite': item.is_favorite,
            'is_sensitive': item.is_sensitive,
            'created_at': item.created_at.isoformat(),
            'updated_at': item.updated_at.isoformat()
        } for item in items]
    
    def _get_file_metadata(self, user_id: int) -> list:
        """Get file metadata for backup"""
        files = VaultFile.query.filter_by(user_id=user_id).all()
        return [{
            'id': file.id,
            'filename': file.filename,
            'file_size': file.file_size,
            'mime_type': file.mime_type,
            'uploaded_at': file.uploaded_at.isoformat()
        } for file in files]
    
    def _get_notes(self, user_id: int) -> list:
        """Get notes for backup"""
        notes = Note.query.filter_by(user_id=user_id).all()
        return [{
            'id': note.id,
            'title': note.title,
            'content': note.content,
            'category': note.category,
            'tags': note.tags,
            'is_archived': note.is_archived,
            'created_at': note.created_at.isoformat(),
            'updated_at': note.updated_at.isoformat()
        } for note in notes]
    
    def _get_settings(self, user_id: int) -> dict:
        """Get user settings for backup"""
        from models.security_setting import SecuritySetting
        setting = SecuritySetting.query.filter_by(user_id=user_id).first()
        
        if setting:
            return {
                'session_timeout_minutes': setting.session_timeout_minutes,
                'max_login_attempts': setting.max_login_attempts,
                'lockout_duration_minutes': setting.lockout_duration_minutes,
                'two_factor_enabled': setting.two_factor_enabled
            }
        return {}
    
    def _restore_items(self, user_id: int, items: list) -> list:
        """Restore vault items from backup"""
        restored = []
        
        for item_data in items:
            # Check if item exists
            existing = VaultItem.query.filter_by(
                user_id=user_id,
                label=item_data['label'],
                category=item_data['category']
            ).first()
            
            if existing:
                # Update existing
                existing.encrypted_value = item_data['encrypted_value']
                existing.notes = item_data.get('notes')
                existing.is_favorite = item_data.get('is_favorite', False)
                existing.is_sensitive = item_data.get('is_sensitive', False)
                existing.updated_at = datetime.utcnow()
                restored.append(existing)
            else:
                # Create new
                new_item = VaultItem(
                    user_id=user_id,
                    category=item_data['category'],
                    label=item_data['label'],
                    encrypted_value=item_data['encrypted_value'],
                    notes=item_data.get('notes'),
                    is_favorite=item_data.get('is_favorite', False),
                    is_sensitive=item_data.get('is_sensitive', False),
                    created_at=datetime.fromisoformat(item_data['created_at']),
                    updated_at=datetime.fromisoformat(item_data['updated_at'])
                )
                db.session.add(new_item)
                restored.append(new_item)
        
        db.session.commit()
        return restored
    
    def _restore_notes(self, user_id: int, notes: list) -> list:
        """Restore notes from backup"""
        restored = []
        
        for note_data in notes:
            existing = Note.query.filter_by(
                user_id=user_id,
                title=note_data['title']
            ).first()
            
            if existing:
                existing.content = note_data['content']
                existing.category = note_data.get('category')
                existing.tags = note_data.get('tags')
                existing.is_archived = note_data.get('is_archived', False)
                existing.updated_at = datetime.utcnow()
                restored.append(existing)
            else:
                new_note = Note(
                    user_id=user_id,
                    title=note_data['title'],
                    content=note_data['content'],
                    category=note_data.get('category'),
                    tags=note_data.get('tags'),
                    is_archived=note_data.get('is_archived', False),
                    created_at=datetime.fromisoformat(note_data['created_at']),
                    updated_at=datetime.fromisoformat(note_data['updated_at'])
                )
                db.session.add(new_note)
                restored.append(new_note)
        
        db.session.commit()
        return restored

# Singleton instance
backup_service = BackupService()