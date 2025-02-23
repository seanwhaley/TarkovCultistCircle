"""Development Configuration."""
from .default import Config

class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    TESTING = False
    
    # Rate limiting - disabled in development
    RATE_LIMIT_ENABLED = False
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_STRATEGY = "fixed-window"
    
    # Logging - verbose in development
    LOG_LEVEL = 'DEBUG'
    LOG_FORMAT = 'text'
    LOG_JSON_INDENT = 2