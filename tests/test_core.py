import unittest
from unittest.mock import patch, MagicMock
import pytest
import time
from datetime import datetime, timedelta
from src.core.cache import Cache, cached
from src.core.limiter import RateLimiter, rate_limit
from src.core.decorators import db_transaction, validate_form_data
from src.application.app_factory import ApplicationFactory
from src.config import Config
from neo4j import GraphDatabase
from src.app import app, get_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def db():
    driver = GraphDatabase.driver(
        app.config['NEO4J_URI'],
        auth=(app.config['NEO4J_USER'], app.config['NEO4J_PASSWORD'])
    )
    yield driver
    driver.close()

class TestCache(unittest.TestCase):
    def setUp(self):
        self.cache = Cache()

    def test_set_get(self):
        self.cache.set('test_key', 'test_value', 1)
        self.assertEqual(self.cache.get('test_key'), 'test_value')

    def test_expiration(self):
        self.cache.set('test_key', 'test_value', 0.1)
        time.sleep(0.2)
        self.assertIsNone(self.cache.get('test_key'))

    def test_delete(self):
        self.cache.set('test_key', 'test_value', 1)
        self.cache.delete('test_key')
        self.assertIsNone(self.cache.get('test_key'))

    def test_clear(self):
        self.cache.set('key1', 'value1', 1)
        self.cache.set('key2', 'value2', 1)
        self.cache.clear()
        self.assertIsNone(self.cache.get('key1'))
        self.assertIsNone(self.cache.get('key2'))

    def test_cached_decorator(self):
        call_count = 0

        @cached(ttl=1)
        def test_function(arg):
            nonlocal call_count
            call_count += 1
            return f"result_{arg}"

        # First call should execute the function
        result1 = test_function("test")
        self.assertEqual(result1, "result_test")
        self.assertEqual(call_count, 1)

        # Second call should return cached result
        result2 = test_function("test")
        self.assertEqual(result2, "result_test")
        self.assertEqual(call_count, 1)

        # Different argument should execute function again
        result3 = test_function("different")
        self.assertEqual(result3, "result_different")
        self.assertEqual(call_count, 2)

class TestRateLimiter(unittest.TestCase):
    def setUp(self):
        self.limiter = RateLimiter(max_requests=2, time_window=1)

    def test_rate_limit(self):
        # First two requests should succeed
        self.assertTrue(self.limiter.allow_request('test_user'))
        self.assertTrue(self.limiter.allow_request('test_user'))
        
        # Third request should be blocked
        self.assertFalse(self.limiter.allow_request('test_user'))

        # After time window, should allow requests again
        time.sleep(1.1)
        self.assertTrue(self.limiter.allow_request('test_user'))

    def test_different_users(self):
        self.assertTrue(self.limiter.allow_request('user1'))
        self.assertTrue(self.limiter.allow_request('user1'))
        self.assertFalse(self.limiter.allow_request('user1'))
        
        # Different user should have separate limit
        self.assertTrue(self.limiter.allow_request('user2'))

    def test_rate_limit_decorator(self):
        call_count = 0

        @rate_limit(max_requests=2, time_window=1)
        def test_function():
            nonlocal call_count
            call_count += 1
            return "success"

        # First two calls should succeed
        self.assertEqual(test_function(), "success")
        self.assertEqual(test_function(), "success")
        
        # Third call should raise exception
        with self.assertRaises(Exception):
            test_function()

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
        def test_function(db):
            return db.query("RETURN 1 as n")

        with patch('src.core.db.Neo4jConnection') as mock_db:
            mock_db.return_value.query.return_value = [{'n': 1}]
            result = test_function(mock_db())
            self.assertEqual(result[0]['n'], 1)

    def test_validate_form_data(self):
        test_schema = {
            'name': str,
            'age': int,
            'email': str
        }

        @validate_form_data(test_schema)
        def test_function(data):
            return data

        # Test valid data
        valid_data = {
            'name': 'Test User',
            'age': 25,
            'email': 'test@example.com'
        }
        result = test_function(valid_data)
        self.assertEqual(result, valid_data)

        # Test invalid data
        invalid_data = {
            'name': 'Test User',
            'age': 'invalid',
            'email': 'test@example.com'
        }
        with self.assertRaises(ValueError):
            test_function(invalid_data)

class TestCore(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        
    def test_index_route(self):
        response = self.app.get('/')
        assert response.status_code == 200
        
    def test_optimize_route(self):
        response = self.app.get('/optimize')
        assert response.status_code == 200
        
    def test_items_route(self):
        response = self.app.get('/items')
        assert response.status_code == 200

    def test_db_connection(self, db):
        with db.session() as session:
            result = session.run("RETURN 1 as num")
            assert result.single()["num"] == 1

    def test_404_handler(self):
        response = self.app.get('/nonexistent')
        assert response.status_code == 404

if __name__ == '__main__':
    unittest.main()