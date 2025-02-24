"""Application configuration module."""
import os
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class BaseConfig:
    """Base configuration with shared settings."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = False
    TESTING = False

    # Database settings
    NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')
    NEO4J_MAX_POOL_SIZE = int(os.getenv('NEO4J_MAX_POOL_SIZE', '50'))

    # API settings
    API_PREFIX = '/api'
    API_VERSION = 'v1'
    API_RATE_LIMIT = int(os.getenv('API_RATE_LIMIT', '1000'))
    API_REFRESH_LIMIT = int(os.getenv('API_REFRESH_LIMIT', '20'))

    # Rate limiting settings
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_DEFAULT = int(os.getenv('RATE_LIMIT_DEFAULT', '1000'))
    RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '3600'))
    RATE_LIMIT_STRATEGY = 'fixed-window'
    RATELIMIT_STORAGE_URL = 'memory://'

    # Logging settings
    LOG_DIR = os.getenv('LOG_DIR', 'logs')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_MAX_SIZE = int(os.getenv('LOG_MAX_SIZE', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '10'))
    LOG_JSON_INDENT = None if os.getenv('ENVIRONMENT') == 'production' else 2

    # Security settings
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    RATE_LIMIT_ENABLED = False
    LOG_LEVEL = 'DEBUG'
    LOG_JSON_INDENT = 2

class TestingConfig(BaseConfig):
    """Test configuration."""
    TESTING = True
    DEBUG = True
    RATE_LIMIT_ENABLED = False
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(BaseConfig):
    """Production configuration."""
    RATE_LIMIT_ENABLED = True
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    LOG_JSON_INDENT = None

def get_config():
    """Get configuration instance based on environment."""
    env = os.getenv('FLASK_ENV', 'development')
    configs = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    return configs.get(env, DevelopmentConfig)

# Default to development config
Config = get_config()

__all__ = ['Config', 'get_config', 'BaseConfig', 'DevelopmentConfig', 'TestingConfig', 'ProductionConfig']