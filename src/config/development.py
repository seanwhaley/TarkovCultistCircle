"""Development Configuration."""
from .default import Config

class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    TESTING = False
    
    # Rate limiting - disabled in development
    RATE_LIMIT_ENABLED = False
    RATE_LIMIT_DEFAULT = 1000
    RATE_LIMIT_WINDOW = 3600
    
    # Logging - verbose in development
    LOG_LEVEL = 'DEBUG'
    LOG_FORMAT = 'text'
    LOG_JSON_INDENT = 2