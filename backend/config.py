"""
StockVision - Flask Configuration
"""
import os

# Base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration"""
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'stockvision-dev-secret-key-2024'
    
    # Database - supports both SQLite (dev) and PostgreSQL (prod)
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        # Fix Heroku's postgres:// to postgresql://
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'stockvision.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    # SESSION_TYPE = 'filesystem'  # Disabled for cloud deployment (Render has ephemeral storage)
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    # Static files - point to existing assets folder
    STATIC_FOLDER = os.path.join(os.path.dirname(BASE_DIR), 'assets')
    
    # Template folder
    TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # Secret key is validated at runtime, not at import time
    @property
    def SECRET_KEY(self):
        secret = os.environ.get('SECRET_KEY')
        if not secret:
            raise ValueError("SECRET_KEY environment variable is required in production!")
        return secret
    
    # Secure session cookies
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
