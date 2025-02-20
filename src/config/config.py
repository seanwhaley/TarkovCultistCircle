import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Base configuration class.
    """
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')
    DEBUG = False
    TESTING = False
    NEO4J_URI = os.getenv('NEO4J_URI')
    NEO4J_USER = os.getenv('NEO4J_USER')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
    GRAPHQL_ENDPOINT = os.getenv('GRAPHQL_ENDPOINT', 'https://api.tarkov.dev/graphql')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """
    Development configuration class.
    """
    DEBUG = True

class TestingConfig(Config):
    """
    Testing configuration class.
    """
    TESTING = True
    DEBUG = True
    NEO4J_URI = os.getenv('TEST_NEO4J_URI', 'bolt://localhost:7688')

class ProductionConfig(Config):
    """
    Production configuration class.
    """
    DEBUG = False
    LOG_LEVEL = 'ERROR'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
