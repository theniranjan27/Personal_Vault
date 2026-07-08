from config.config import Config
import os

class DevelopmentConfig(Config):
    """Development configuration"""
    
    DEBUG = True
    TESTING = False
    
    # Database - use SQLite for development if not specified
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///vault_dev.db'
    
    # Session
    SESSION_COOKIE_SECURE = False  # Disable HTTPS in development
    
    # CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # CORS
    CORS_ORIGINS = '*'
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    
    # Rate Limiting
    RATELIMIT_ENABLED = False
    
    # File Upload
    UPLOAD_FOLDER = 'temp'
    
    def __init__(self):
        # Ensure required directories exist
        import os
        for directory in ['temp', 'backups', 'logs']:
            if not os.path.exists(directory):
                os.makedirs(directory)