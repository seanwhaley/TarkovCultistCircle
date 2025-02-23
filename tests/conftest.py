"""Shared test configuration and fixtures."""
import pytest
from src.application.app_factory import ApplicationFactory
from src.core.db import Neo4jConnection
from src.config import Config

@pytest.fixture
def app():
    """Create application for testing."""
    app = ApplicationFactory.create_app(Config)
    app.config.update({
        'TESTING': True,
        'NEO4J_URI': 'bolt://localhost:7687',
        'NEO4J_USER': 'neo4j',
        'NEO4J_PASSWORD': 'test',
        'RATE_LIMIT_ENABLED': False,
        'RATELIMIT_STORAGE_URL': 'memory://',
        'RATELIMIT_STRATEGY': 'fixed-window'
    })
    return app

@pytest.fixture
def client(app):
    """Create test client."""
    with app.test_client() as client:
        yield client

@pytest.fixture
def db(app):
    """Create database connection for testing."""
    db = Neo4jConnection(
        uri=app.config['NEO4J_URI'],
        user=app.config['NEO4J_USER'],
        password=app.config['NEO4J_PASSWORD']
    )
    # Clear test data before each test
    db.query("MATCH (n) DETACH DELETE n")
    yield db
    # Clean up after tests
    db.query("MATCH (n) DETACH DELETE n")
    db.close()

@pytest.fixture
def sample_items():
    """Sample item data for testing."""
    return [
        {
            "uid": "item1",
            "name": "Test Item 1",
            "base_price": 1000,
            "blacklisted": False,
            "locked": False
        },
        {
            "uid": "item2",
            "name": "Test Item 2",
            "base_price": 2000,
            "blacklisted": True,
            "locked": False
        }
    ]
