import unittest
from datetime import datetime, timedelta
import json
from src.application.app_factory import ApplicationFactory
from src.config import Config

class TestHistory(unittest.TestCase):
    def setUp(self):
        self.app = ApplicationFactory.create_app(Config)
        self.app.config.update({
            'TESTING': True,
            'WTF_CSRF_ENABLED': False,
            'NEO4J_URI': 'bolt://localhost:7687',
            'NEO4J_USER': 'neo4j',
            'NEO4J_PASSWORD': 'test'
        })
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        if self.app_context:
            self.app_context.pop()

    def test_history_index(self):
        response = self.client.get('/history/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Price History', response.data)

    def test_item_history(self):
        # Test getting history for a specific item
        response = self.client.get('/history/item/test_item')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('history', data)
        self.assertIn('itemDetails', data)

    def test_market_history(self):
        response = self.client.get('/history/market')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('marketHistory', data)

    def test_history_export(self):
        response = self.client.get('/history/export')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        data = json.loads(response.data)
        self.assertIn('history', data)

    def test_add_history_entry(self):
        data = {
            'itemId': 'test_item',
            'price': 15000,
            'timestamp': datetime.utcnow().isoformat()
        }
        response = self.client.post('/history/add',
                                  json=data,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result['success'])

    def test_clear_history(self):
        # Test clearing history for a specific item
        response = self.client.post('/history/clear/test_item')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertTrue(result['success'])

    def test_invalid_item_history(self):
        response = self.client.get('/history/item/nonexistent_item')
        self.assertEqual(response.status_code, 404)

    def test_invalid_history_entry(self):
        # Test adding invalid history entry
        data = {
            'itemId': 'test_item',
            'price': 'invalid_price',  # Should be a number
            'timestamp': datetime.utcnow().isoformat()
        }
        response = self.client.post('/history/add',
                                  json=data,
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.data)
        self.assertFalse(result['success'])

    def test_date_range_history(self):
        # Test getting history within a date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        response = self.client.get(
            f'/history/range?start={start_date.isoformat()}&end={end_date.isoformat()}'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('history', data)

    def test_history_aggregation(self):
        # Test history aggregation endpoint
        response = self.client.get('/history/aggregate?period=daily')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('aggregatedHistory', data)

if __name__ == '__main__':
    unittest.main()