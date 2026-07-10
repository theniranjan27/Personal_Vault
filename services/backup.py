import json
import os
import zipfile
import hashlib
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
    
    def calculate_checksum(self, data: str) -> str:
        """Calculate SHA-256 checksum of string data"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def create_backup(self, user_id: int, password: Optional[str] = None,
                      include_files: bool = True, include_settings: bool = True) -> dict:
        """Create a backup of user data"""
        timestamp = datetime.utcnow().isoformat()
        
        # Gather data
        from models.user import User
        user = User.query.get(user_id)
        
        items_data = self._get_items(user_id)
        notes_data = self._get_notes(user_id)
        
        # Calculate integrity checksum of plaintext records
        records_str = json.dumps({'items': items_data, 'notes': notes_data}, default=str)
        integrity_checksum = self.calculate_checksum(records_str)
        
        backup_data = {
            'type': 'vault_backup',
            'version': '1.0',
            'timestamp': timestamp,
            'user_id': user_id,
            'items': items_data,
            'files': self._get_file_metadata(user_id) if include_files else [],
            'notes': notes_data,
            'settings': self._get_settings(user_id) if include_settings else {},
            'metadata': {
                'version': '1.0',
                'timestamp': timestamp,
                'user_id': user_id,
                'item_count': len(items_data) + len(notes_data),
                'integrity_checksum': integrity_checksum
            },
            'user': {
                'username': user.username if user else 'admin',
                'email': user.email if user else 'admin@example.com',
                'full_name': user.full_name if user else 'Admin User'
            }
        }
        
        # Serialize and encrypt
        json_data = json.dumps(backup_data, default=str)
        
        # Always encrypt backups
        encrypted_data = encryption_service.encrypt(json_data)
        
        # Calculate checksum on encrypted data
        checksum = self.calculate_checksum(encrypted_data)
        
        # Save backup file
        now = datetime.utcnow()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H-%M-%S')
        file_name = f"personal_vault_backup_{date_str}_{time_str}.vault"
        
        user_dir = os.path.join(self.backup_dir, f"user_{user_id}")
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        file_path = os.path.join(user_dir, file_name)
        
        with open(file_path, 'w') as f:
            f.write(encrypted_data)
        
        # Log backup
        backup_log = BackupLog(
            user_id=user_id,
            file_name=file_name,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            items_count=len(backup_data['items']) + len(backup_data['notes']),
            checksum=checksum,
            status='Not Verified',
            created_at=now,
            last_verified_at=None,
            download_count=0
        )
        db.session.add(backup_log)
        db.session.commit()
        
        # Audit log
        audit_service.log_action(
            user_id=user_id,
            action='backup',
            details={
                'file_name': file_name,
                'items': len(backup_data['items']),
                'notes': len(backup_data['notes'])
            }
        )
        
        return {
            'file_name': file_name,
            'file_path': file_path,
            'items': len(backup_data['items']) + len(backup_data['notes']),
            'size': os.path.getsize(file_path),
            'checksum': checksum
        }
    
    def restore_backup(self, user_id: int, file_name: str, 
                       password: Optional[str] = None) -> dict:
        """Restore from a backup"""
        # Find backup log
        backup_log = BackupLog.query.filter_by(
            user_id=user_id,
            file_name=file_name
        ).first()
        
        if not backup_log:
            raise ValueError("Backup not found")
        
        # Read backup file
        filepath = backup_log.file_path
        
        if not os.path.exists(filepath):
            raise ValueError("Backup file not found")
        
        with open(filepath, 'r') as f:
            encrypted_data = f.read()
        
        # Verify checksum before decrypting/restoring
        current_checksum = self.calculate_checksum(encrypted_data)
        if current_checksum != backup_log.checksum:
            backup_log.status = 'Corrupted'
            db.session.commit()
            raise ValueError("Backup checksum mismatch! Rejecting corrupted or invalid backup file.")
        
        # Decrypt
        try:
            json_data = encryption_service.decrypt(encrypted_data)
            if not json_data:
                raise ValueError()
        except Exception:
            backup_log.status = 'Corrupted'
            db.session.commit()
            raise ValueError("Decryption failed. Unauthorized or corrupted backup file.")
        
        # Parse backup data
        backup_data = json.loads(json_data)
        
        # Validate backup
        if backup_data.get('type') != 'vault_backup':
            raise ValueError("Invalid backup file")
            
        # Verify integrity checksum of restored records
        metadata_block = backup_data.get('metadata', {})
        if 'integrity_checksum' in metadata_block:
            records_str = json.dumps({
                'items': backup_data.get('items', []),
                'notes': backup_data.get('notes', [])
            }, default=str)
            calculated_checksum = self.calculate_checksum(records_str)
            if calculated_checksum != metadata_block['integrity_checksum']:
                backup_log.status = 'Corrupted'
                db.session.commit()
                raise ValueError("Plaintext integrity checksum mismatch! File content is corrupted.")
        
        # Restore data
        restored_items = self._restore_items(user_id, backup_data.get('items', []))
        restored_notes = self._restore_notes(user_id, backup_data.get('notes', []))
        
        # Update backup log status to Verified since it restored successfully
        backup_log.status = 'Verified'
        backup_log.last_verified_at = datetime.utcnow()
        db.session.commit()
        
        # Audit log
        audit_service.log_action(
            user_id=user_id,
            action='restore',
            details={
                'file_name': file_name,
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
        
        return [log.to_dict() for log in logs]
    
    def delete_backup(self, user_id: int, file_name: str) -> bool:
        """Delete a backup"""
        backup_log = BackupLog.query.filter_by(
            user_id=user_id,
            file_name=file_name
        ).first()
        
        if not backup_log:
            return False
        
        # Delete file
        filepath = backup_log.file_path
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Delete log
        db.session.delete(backup_log)
        db.session.commit()
        
        # Audit log
        audit_service.log_action(
            user_id=user_id,
            action='delete_backup',
            details={'file_name': file_name}
        )
        
        return True
    
    def export_backup(self, user_id: int, file_name: str) -> bytes:
        """Export backup as downloadable file"""
        backup_log = BackupLog.query.filter_by(
            user_id=user_id,
            file_name=file_name
        ).first()
        
        if not backup_log:
            raise ValueError("Backup not found")
        
        filepath = backup_log.file_path
        
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
            'extra': item.get_extra(),
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
                if 'extra' in item_data:
                    existing.set_extra(item_data['extra'])
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
                if 'extra' in item_data:
                    new_item.set_extra(item_data['extra'])
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

    def encrypt_backup(self, data: dict) -> str:
        """Encrypt backup data"""
        json_data = json.dumps(data)
        return encryption_service.encrypt(json_data)

    def decrypt_backup(self, encrypted_data: str) -> dict:
        """Decrypt backup data"""
        json_data = encryption_service.decrypt(encrypted_data)
        return json.loads(json_data)

# Singleton instance
backup_service = BackupService()