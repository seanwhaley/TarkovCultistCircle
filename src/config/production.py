"""Production Configuration."""
from .default import Config

class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Rate limiting - enabled with strict limits
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_DEFAULT = 1000
    RATE_LIMIT_WINDOW = 3600
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = 'json'
    LOG_JSON_INDENT = None
