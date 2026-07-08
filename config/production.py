from config.config import Config
import os

class ProductionConfig(Config):
    """Production configuration"""
    
    DEBUG = False
    TESTING = False
    
    # Session
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING')
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '100/hour')
    RATELIMIT_LOGIN = os.environ.get('RATELIMIT_LOGIN', '5/15minute')
    
    # File Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024))  # 50MB
    
    # Security
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Admin
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    ADMIN_FULL_NAME = os.environ.get('ADMIN_FULL_NAME')
    
    def __init__(self):
        # Validate required environment variables
        required_vars = [
            'SECRET_KEY',
            'ENCRYPTION_KEY',
            'DATABASE_URL'
        ]
        
        missing = [var for var in required_vars if not os.environ.get(var)]
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
        
        # Ensure required directories exist
        import os
        for directory in ['uploads', 'backups', 'logs']:
            if not os.path.exists(directory):
                os.makedirs(directory)