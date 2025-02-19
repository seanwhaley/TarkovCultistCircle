import os
from dotenv import load_dotenv

load_dotenv()

# GraphQL Queries
ITEMS_QUERY = """
query getItems($lang: String!, $ids: [ID!]) {
    items(lang: $lang, ids: $ids) {
        id name basePrice
        buyFor { priceRUB vendor { name } }
        categories { name }
        fleaMarketFee
        sellFor { priceRUB vendor { name } }
        updated weight
    }
}
"""

ITEM_BY_ID_QUERY = """
query getItem($id: ID!, $lang: String!) {
    item(id: $id, lang: $lang) {
        id name basePrice
        buyFor { priceRUB vendor { name } }
        categories { name }
        fleaMarketFee
        sellFor { priceRUB vendor { name } }
        updated weight
    }
}
"""

class Config:
    """Base configuration class"""
    # Flask settings
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev')
    DEBUG = False
    TESTING = False
    
    # Database settings
    NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://neo4j_db:7687')
    NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '')
    
    # API settings
    GRAPHQL_ENDPOINT = os.getenv('GRAPHQL_ENDPOINT', 'https://api.tarkov.dev/graphql')
    GRAPHQL_QUERY = ITEMS_QUERY  # Default query
    GRAPHQL_VARIABLES = {
        'lang': os.getenv('GRAPHQL_LANG', 'en'),
        'ids': None
    }
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    
    # Docker settings
    DOCKER_NEO4J_AUTH = os.getenv('DOCKER_NEO4J_AUTH', 'neo4j/password')
    DOCKER_NEO4J_MEMORY_HEAP_INITIAL = os.getenv('DOCKER_NEO4J_server_memory_heap_initial__size', '512M')
    DOCKER_NEO4J_MEMORY_HEAP_MAX = os.getenv('DOCKER_NEO4J_server_memory_heap_max__size', '2G')
    DOCKER_NEO4J_MEMORY_PAGECACHE = os.getenv('DOCKER_NEO4J_server_memory_pagecache_size', '1G')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    NEO4J_URI = os.getenv('TEST_NEO4J_URI', 'bolt://localhost:7688')


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'ERROR'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

from .config import Config, config

__all__ = ['Config', 'config']
