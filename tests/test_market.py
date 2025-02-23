import unittest
import json
from datetime import datetime, timedelta
import pytest
from src.application.app_factory import ApplicationFactory
from src.core.db import Neo4jConnection
from src.config import Config
from src.services.market import MarketService

@pytest.fixture
def app():
    app = ApplicationFactory.create_app(Config)
    app.config.update({
        'TESTING': True,
        'NEO4J_URI': 'bolt://localhost:7687',
        'NEO4J_USER': 'neo4j',
        'NEO4J_PASSWORD': 'test'
    })
    return app

@pytest.fixture
def db(app):
    db = Neo4jConnection(
        uri=app.config['NEO4J_URI'],
        user=app.config['NEO4J_USER'],
        password=app.config['NEO4J_PASSWORD'],
        database='neo4j'
    )
    # Clear test data
    db.query("MATCH (n) DETACH DELETE n")
    yield db
    # Clean up after tests
    db.query("MATCH (n) DETACH DELETE n")
    db.close()

@pytest.fixture
def sample_market_data(db):
    """Create sample market data for tests."""
    test_data = [
        {
            "item_id": "item1",
            "price": 1500,
            "timestamp": datetime.utcnow()
        },
        {
            "item_id": "item2",
            "price": 2500,
            "timestamp": datetime.utcnow() - timedelta(hours=1)
        }
    ]
    
    # Insert test market data
    for data in test_data:
        db.query(
            """
            MATCH (i:Item {uid: $item_id})
            CREATE (p:Price {value: $price, timestamp: $timestamp})
            CREATE (i)-[:HAS_PRICE]->(p)
            """,
            parameters=data
        )
    return test_data

class TestMarket(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def setup(self, app, db, sample_market_data):
        self.app = app
        self.db = db
        self.market_data = sample_market_data
        self.market = MarketService(self.db)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        if self.app_context:
            self.app_context.pop()

    def test_market_index(self):
        response = self.client.get('/market/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Market Overview', response.data)

    def test_price_check(self):
        data = {'itemId': 'test_item'}
        response = self.client.post('/market/check-price',
                                  json=data,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result['success'])
        self.assertIn('currentPrice', result)

    def test_market_trends(self):
        response = self.client.get('/market/trends')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('trends', data)
        self.assertIn('timestamp', data)

    def test_price_alerts(self):
        # Test setting a price alert
        alert_data = {
            'itemId': 'test_item',
            'targetPrice': 1500,
            'condition': 'below',
            'email': 'test@example.com'
        }
        response = self.client.post('/market/alerts/create',
                                  json=alert_data,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result['success'])

        # Test getting active alerts
        response = self.client.get('/market/alerts')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('alerts', data)

    def test_trader_prices(self):
        response = self.client.get('/market/trader-prices/test_item')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('traders', data)

    def test_price_history(self):
        response = self.client.get('/market/history/test_item')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('history', data)
        self.assertIn('item', data)

    def test_price_prediction(self):
        response = self.client.get('/market/predict/test_item')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('prediction', data)
        self.assertIn('confidence', data)

    def test_market_summary(self):
        response = self.client.get('/market/summary')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('topMovers', data)
        self.assertIn('recentUpdates', data)
        self.assertIn('marketHealth', data)

    def test_market_search(self):
        search_data = {'query': 'test'}
        response = self.client.post('/market/search',
                                  json=search_data,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('results', result)

    def test_market_filters(self):
        filter_data = {
            'minPrice': 1000,
            'maxPrice': 5000,
            'category': 'weapons',
            'sort': 'price'
        }
        response = self.client.post('/market/filter',
                                  json=filter_data,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('items', result)

    def test_invalid_price_check(self):
        data = {'itemId': 'nonexistent_item'}
        response = self.client.post('/market/check-price',
                                  json=data,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 404)
        result = json.loads(response.data)
        self.assertFalse(result['success'])

    def test_invalid_alert_setup(self):
        alert_data = {
            'itemId': 'test_item',
            'targetPrice': 'invalid',  # Should be a number
            'condition': 'invalid',    # Should be 'above' or 'below'
            'email': 'invalid_email'   # Should be valid email format
        }
        response = self.client.post('/market/alerts/create',
                                  json=alert_data,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.data)
        self.assertFalse(result['success'])

if __name__ == '__main__':
    unittest.main()