"""Application settings and configuration."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

class BaseConfig:
    """Base configuration."""
    DEBUG = False
    TESTING = False
    RATE_LIMIT_ENABLED = False

class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True

class TestingConfig(BaseConfig):
    """Test configuration."""
    TESTING = True
    DEBUG = True

class ProductionConfig(BaseConfig):
    """Production configuration."""
    RATE_LIMIT_ENABLED = True

@dataclass
class Settings:
    """Application settings loaded from environment variables."""
    
    # Database settings
    neo4j_uri: str = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user: str = os.getenv('NEO4J_USER', 'neo4j')
    neo4j_password: str = os.getenv('NEO4J_PASSWORD', '')
    
    # API settings
    tarkov_api_url: str = os.getenv('TARKOV_API_URL', 'https://api.tarkov.dev/graphql')
    api_timeout: int = int(os.getenv('API_TIMEOUT', '30'))
    api_rate_limit: int = int(os.getenv('API_RATE_LIMIT', '1000'))
    api_refresh_interval: int = int(os.getenv('API_REFRESH_INTERVAL', '300'))
    
    # Application settings
    debug: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    secret_key: str = os.getenv('SECRET_KEY', 'default-secret-key')
    env: str = os.getenv('FLASK_ENV', 'development')
