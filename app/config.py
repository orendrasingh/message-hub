"""
Application configuration classes
"""

import os
import secrets
from datetime import timedelta


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    DB_PATH = os.environ.get('DB_PATH', 'whatsapp.db')
    
    # Evolution API Configuration - MUST be set in .env file
    EVOLUTION_API_URL = os.environ.get('EVOLUTION_API_URL', 'http://localhost:8340')
    EVOLUTION_GLOBAL_KEY = os.environ.get('EVOLUTION_GLOBAL_KEY')  # No fallback - must be in .env
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Email Configuration - MUST be set in .env file for production
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
    EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')  # No fallback
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')  # No fallback
    
    # Security
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file upload for media
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'memory://'
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
    MEDIA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads', 'media')
    ALLOWED_EXTENSIONS = {'csv', 'txt'}
    ALLOWED_MEDIA_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'}
    
    # Media file size limits
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB for images
    MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB for videos
    
    @staticmethod
    def init_app(app):
        """Initialize app-specific configuration"""
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    
    # Relaxed rate limits for development
    RATELIMIT_DEFAULT = ["2000 per day", "500 per hour"]


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    
    # Strict rate limits for production
    RATELIMIT_DEFAULT = ["1000 per day", "200 per hour"]
    
    # Additional security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY', 
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; font-src 'self' https://cdn.jsdelivr.net;"
    }


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DB_PATH = ':memory:'  # Use in-memory database for tests
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
