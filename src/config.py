"""Application configuration."""

class Config:
    # Core settings
    SECRET_KEY = 'your_secret_key'
    DEBUG = False

    # Database settings
    NEO4J_URI = 'bolt://localhost:7687'
    NEO4J_USER = 'neo4j'
    NEO4J_PASSWORD = 'your_password'
    NEO4J_MAX_CONNECTION_POOL_SIZE = 50

    # API settings
    API_RATE_LIMIT = 1000
    API_REFRESH_LIMIT = 20

    # Rate limiting settings
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_STRATEGY = "fixed-window"
    RATELIMIT_DEFAULT = "1000 per hour"

class DevelopmentConfig(Config):
    DEBUG = True
    RATE_LIMIT_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    RATE_LIMIT_ENABLED = True
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Strict'
