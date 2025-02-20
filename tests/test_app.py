import pytest
from src.application.app_factory import ApplicationFactory

@pytest.fixture
def client():
    test_app = ApplicationFactory.create_app()
    test_app.config['TESTING'] = True
    with test_app.test_client() as client:
        yield client

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to Tarkov Cultist Circle" in response.data