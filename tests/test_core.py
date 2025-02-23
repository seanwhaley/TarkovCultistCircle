"""Tests for core functionality."""
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from src.core.limiter import RateLimiter
from src.core.decorators import db_transaction, validate_form_data
from src.core.metrics import MetricsCollector
from src.application.app_factory import ApplicationFactory
from src.config import Config

class TestRateLimiter(unittest.TestCase):
    def setUp(self):
        self.limiter = RateLimiter()

    def test_rate_limit_basic(self):
        request = MagicMock()
        request.client.host = '127.0.0.1'
        request.url.path = '/test'

        # First request should not be limited
        is_limited, info = self.limiter.is_rate_limited(request)
        self.assertFalse(is_limited)
        self.assertEqual(info['limit'], 1000)
        self.assertEqual(info['remaining'], 999)

    def test_docs_routes_not_limited(self):
        request = MagicMock()
        request.url.path = '/docs'
        is_limited, _ = self.limiter.is_rate_limited(request)
        self.assertFalse(is_limited)

class TestDecorators(unittest.TestCase):
    def setUp(self):
        self.app = ApplicationFactory.create_app(Config)
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        if self.app_context:
            self.app_context.pop()

    def test_db_transaction(self):
        @db_transaction
        def test_func(db):
            return db.query("RETURN 1")

        mock_db = MagicMock()
        test_func(db=mock_db)
        mock_db.transaction.assert_called_once()

    def test_validate_form_data(self):
        schema = {'name': str, 'age': int}

        @validate_form_data(schema)
        def test_func(data):
            return data

        valid_data = {'name': 'Test', 'age': 25}
        self.assertEqual(test_func(valid_data), valid_data)

        invalid_data = {'name': 'Test', 'age': '25'}
        with self.assertRaises(ValueError):
            test_func(invalid_data)

class TestMetrics(unittest.TestCase):
    def setUp(self):
        self.metrics = MetricsCollector()

    def test_request_counting(self):
        self.metrics.record_request('GET', '/test', 200)
        self.metrics.record_request('GET', '/test', 500)
        
        stats = self.metrics.get_stats()
        self.assertEqual(stats['total_requests'], 2)
        self.assertEqual(stats['total_errors'], 1)
        self.assertEqual(stats['routes']['GET:/test'], 2)
        self.assertEqual(stats['error_routes']['GET:/test'], 1)

if __name__ == '__main__':
    unittest.main()