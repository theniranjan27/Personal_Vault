import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'security-salt-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///vault.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # Session
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = int(os.environ.get('SESSION_TIMEOUT_MINUTES', 15)) * 60
    
    # Security
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
    BCRYPT_ROUNDS = int(os.environ.get('BCRYPT_ROUNDS', 12))
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', 5))
    LOCKOUT_DURATION_MINUTES = int(os.environ.get('LOCKOUT_DURATION_MINUTES', 30))
    
    # File Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'temp'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024))  # 50MB
    ALLOWED_EXTENSIONS = os.environ.get('ALLOWED_EXTENSIONS', 'pdf,doc,docx,xls,xlsx,ppt,pptx,jpg,jpeg,png,gif,webp,txt,md,json,xml,csv,zip,rar,7z')
    
    # CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    
    # Backup
    BACKUP_DIR = os.environ.get('BACKUP_DIR') or 'backups'
    BACKUP_ENCRYPTION_ENABLED = os.environ.get('BACKUP_ENCRYPTION_ENABLED', 'True').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/app.log'
    AUDIT_LOG_FILE = os.environ.get('AUDIT_LOG_FILE') or 'logs/audit.log'
    ERROR_LOG_FILE = os.environ.get('ERROR_LOG_FILE') or 'logs/error.log'
    
    # Rate Limiting
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'True').lower() == 'true'
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '100/hour')
    RATELIMIT_LOGIN = os.environ.get('RATELIMIT_LOGIN', '5/15minute')
    
    # Admin
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    ADMIN_FULL_NAME = os.environ.get('ADMIN_FULL_NAME')
    
    def get_allowed_extensions_list(self):
        """Get allowed extensions as a list"""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(',') if ext.strip()]
    
    def get_upload_folder(self):
        """Get upload folder path"""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), self.UPLOAD_FOLDER)
    
    def get_backup_dir(self):
        """Get backup directory path"""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), self.BACKUP_DIR)
    
    def get_log_dir(self):
        """Get log directory path"""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')