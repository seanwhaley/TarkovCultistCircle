class Config:
    SECRET_KEY = 'your_secret_key'
    NEO4J_URI = 'bolt://localhost:7687'
    NEO4J_USER = 'neo4j'
    NEO4J_PASSWORD = 'your_password'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
