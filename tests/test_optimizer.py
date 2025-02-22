import unittest
import json
from datetime import datetime, timedelta
import pytest
from src.application.app_factory import ApplicationFactory
from src.core.db import Neo4jConnection
from src.config import Config

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
    # Clear test data before each test
    db.query("MATCH (n) DETACH DELETE n")
    yield db
    # Clean up after tests
    db.query("MATCH (n) DETACH DELETE n")
    db.close()

class TestOptimizer(unittest.TestCase):
    def setUp(self):
        self.app = ApplicationFactory.create_app(Config)
        self.app.config.update({
            'TESTING': True,
            'WTF_CSRF_ENABLED': False
        })
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        if self.app_context:
            self.app_context.pop()

    def test_optimize_calculation(self):
        # Test optimization calculation endpoint
        data = {
            'budget': 1000000,
            'maxItems': 3
        }
        response = self.client.post('/optimize/calculate',
                                  json=data,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result['success'])
        self.assertIn('combinations', result)

    def test_item_blacklist(self):
        # Test blacklisting an item
        data = {
            'itemId': 'test_item',
            'duration': 3600  # 1 hour in seconds
        }
        response = self.client.post('/optimize/blacklist',
                                  json=data,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result['success'])

        # Verify item is blacklisted
        response = self.client.get('/optimize/blacklist')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('test_item', [item['id'] for item in result['items']])

    def test_item_lock(self):
        # Test locking an item
        data = {
            'itemId': 'test_item',
            'duration': 3600  # 1 hour in seconds
        }
        response = self.client.post('/optimize/lock',
                                  json=data,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result['success'])

        # Verify item is locked
        response = self.client.get('/optimize/locks')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertIn('test_item', [item['id'] for item in result['items']])

    def test_save_combination(self):
        # Test saving a combination
        data = {
            'items': ['item1', 'item2'],
            'totalValue': 1000000
        }
        response = self.client.post('/optimize/history',
                                  json=data,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result['success'])

        # Verify combination was saved
        response = self.client.get('/optimize/history')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(len(result['combinations']) > 0)

    def test_invalid_optimization_parameters(self):
        # Test with invalid parameters
        data = {
            'budget': -1000,
            'maxItems': 0
        }
        response = self.client.post('/optimize/calculate',
                                  json=data,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.data)
        self.assertFalse(result['success'])

    def test_expired_blacklist(self):
        # Test that expired blacklist items are not returned
        data = {
            'itemId': 'test_item',
            'duration': 1  # 1 second
        }
        response = self.client.post('/optimize/blacklist',
                                  json=data,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Wait for blacklist to expire
        import time
        time.sleep(2)

        # Verify item is no longer blacklisted
        response = self.client.get('/optimize/blacklist')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertNotIn('test_item', [item['id'] for item in result['items']])

    def test_optimization_with_locked_items(self):
        # Test that optimization includes locked items
        # First lock an item
        lock_data = {
            'itemId': 'test_item',
            'duration': 3600
        }
        self.client.post('/optimize/lock',
                        json=lock_data,
                        content_type='application/json')

        # Then run optimization
        opt_data = {
            'budget': 1000000,
            'maxItems': 3
        }
        response = self.client.post('/optimize/calculate',
                                  json=opt_data,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result['success'])
        
        # Verify locked item is included in results
        combinations = result.get('combinations', [])
        if combinations:
            items_in_combinations = [item for combo in combinations for item in combo['items']]
            self.assertIn('test_item', items_in_combinations)

if __name__ == '__main__':
    unittest.main()