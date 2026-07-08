import os
import uuid
import shutil
from typing import Optional, Tuple, BinaryIO
from werkzeug.utils import secure_filename
from flask import current_app
import magic

class FileHandlerService:
    """File handling service for uploads and downloads"""
    
    def __init__(self):
        self.upload_dir = 'temp'
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.allowed_extensions = {
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
            'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg',
            'txt', 'md', 'json', 'xml', 'csv',
            'zip', 'rar', '7z'
        }
        self.ensure_upload_dir()
    
    def ensure_upload_dir(self):
        """Ensure upload directory exists"""
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
    
    def save_file(self, file: BinaryIO, filename: str, user_id: int) -> dict:
        """Save uploaded file securely"""
        # Sanitize filename
        safe_filename = secure_filename(filename)
        
        # Check extension
        ext = safe_filename.split('.')[-1].lower()
        if ext not in self.allowed_extensions:
            raise ValueError(f'File extension not allowed: {ext}')
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]
        stored_filename = f"{unique_id}_{safe_filename}"
        file_path = os.path.join(self.upload_dir, stored_filename)
        
        # Save file
        file.seek(0)
        file.save(file_path)
        
        # Get file info
        file_size = os.path.getsize(file_path)
        
        # Detect MIME type
        mime_type = magic.from_file(file_path, mime=True)
        
        return {
            'filename': safe_filename,
            'stored_filename': stored_filename,
            'file_path': file_path,
            'file_size': file_size,
            'mime_type': mime_type,
            'extension': ext
        }
    
    def get_file(self, file_path: str) -> Tuple[bytes, str]:
        """Get file content and MIME type"""
        if not os.path.exists(file_path):
            raise FileNotFoundError('File not found')
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        mime_type = magic.from_file(file_path, mime=True)
        return content, mime_type
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
    
    def get_file_info(self, file_path: str) -> dict:
        """Get file information"""
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        return {
            'name': os.path.basename(file_path),
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'mime_type': magic.from_file(file_path, mime=True)
        }
    
    def is_allowed_file(self, filename: str) -> bool:
        """Check if file type is allowed"""
        ext = filename.split('.')[-1].lower()
        return ext in self.allowed_extensions
    
    def get_allowed_extensions(self) -> list:
        """Get list of allowed extensions"""
        return sorted(self.allowed_extensions)
    
    def get_max_file_size(self) -> int:
        """Get maximum file size in bytes"""
        return self.max_file_size
    
    def get_max_file_size_mb(self) -> float:
        """Get maximum file size in MB"""
        return self.max_file_size / (1024 * 1024)
    
    def validate_file(self, file: BinaryIO, filename: str) -> dict:
        """Validate file before upload"""
        errors = {}
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > self.max_file_size:
            errors['size'] = f'File size exceeds maximum ({self.get_max_file_size_mb():.0f}MB)'
        
        # Check extension
        if not self.is_allowed_file(filename):
            errors['extension'] = f'File type not allowed. Allowed: {", ".join(self.get_allowed_extensions())}'
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'size': file_size
        }

# Singleton instance
file_handler_service = FileHandlerService()