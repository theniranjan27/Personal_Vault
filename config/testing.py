from config.config import Config
import os

class TestingConfig(Config):
    """Testing configuration"""
    
    TESTING = True
    DEBUG = True
    
    # Database - use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:'
    SQLALCHEMY_ENGINE_OPTIONS = {}
    
    # Session
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CSRF
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing
    
    # CORS
    CORS_ORIGINS = '*'
    
    # Logging
    LOG_LEVEL = 'ERROR'
    
    # Rate Limiting
    RATELIMIT_ENABLED = False
    
    # File Upload
    UPLOAD_FOLDER = 'test_temp'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    
    # Backup
    BACKUP_DIR = 'test_backups'
    BACKUP_ENCRYPTION_ENABLED = False
    
    # Security
    ENCRYPTION_KEY = 'test-encryption-key-32-bytes-long!!!'
    SECRET_KEY = 'test-secret-key'
    
    def __init__(self):
        # Ensure test directories exist
        import os
        for directory in ['test_temp', 'test_backups', 'logs']:
            if not os.path.exists(directory):
                os.makedirs(directory)