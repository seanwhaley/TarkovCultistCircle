import pytest
from src.app import app, get_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['NEO4J_URI'] = 'bolt://localhost:7687'  # Use localhost for tests
    with app.test_client() as client:
        yield client

@pytest.fixture
def db():
    db = get_db()
    yield db
    db.close()

@pytest.fixture
def sample_items():
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
