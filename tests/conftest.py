"""Shared test configuration and fixtures."""
import pytest
from flask import Flask
from src.core.config import Settings
from src.database.neo4j import Neo4jDB
from src.core.limiter import InMemoryRateLimiter

@pytest.fixture
def app():
    """Create application for testing."""
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY='test_key',
        NEO4J_URI='bolt://localhost:7687',
        NEO4J_USER='neo4j',
        NEO4J_PASSWORD='test',
        NEO4J_MAX_POOL_SIZE=5,
        RATE_LIMIT_ENABLED=True,
        RATE_LIMIT_DEFAULT=1000,
        RATE_LIMIT_WINDOW=3600
    )
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def db(app):
    """Create database connection for testing."""
    db = Neo4jDB(
        uri=app.config['NEO4J_URI'],
        user=app.config['NEO4J_USER'],
        password=app.config['NEO4J_PASSWORD']
    )
    # Clear test data
    db.query("MATCH (n) DETACH DELETE n")
    yield db
    # Clean up after tests
    db.query("MATCH (n) DETACH DELETE n")
    db.close()

@pytest.fixture
def rate_limiter():
    """Create rate limiter for testing."""
    return InMemoryRateLimiter()

@pytest.fixture
def sample_items():
    """Sample item data for testing."""
    return [
        {
            "id": "item1",
            "name": "Test Item 1",
            "basePrice": 10000,
            "lastLowPrice": 9500,
            "avg24hPrice": 9750,
            "updated": "2024-01-01T00:00:00Z"
        },
        {
            "id": "item2",
            "name": "Test Item 2",
            "basePrice": 20000,
            "lastLowPrice": 19000,
            "avg24hPrice": 19500,
            "updated": "2024-01-01T00:00:00Z"
        }
    ]
