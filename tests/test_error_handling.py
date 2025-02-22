import unittest
from unittest.mock import patch
import pytest
from src.application.app_factory import ApplicationFactory
from src.core.db import Neo4jConnection
from src.config import Config
from neo4j.exceptions import ServiceUnavailable, AuthError

class ErrorHandlingTestCase(unittest.TestCase):
    """
    Test case for Flask application error handling.
    """
    def setUp(self):
        """
        Set up the test client.
        """
        self.app = ApplicationFactory.create_app(Config)
        self.app.config.update({
            'TESTING': True,
            'NEO4J_URI': 'bolt://localhost:7687',
            'NEO4J_USER': 'neo4j',
            'NEO4J_PASSWORD': 'test'
        })
        self.client = self.app.test_client()

    def test_404_error(self):
        """
        Test 404 error handling.

        Asserts:
            The response status code is 404.
            The response data contains 'Not Found'.
        """
        response = self.client.get('/nonexistent_route')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Not Found', response.data)

    def test_500_error(self):
        """
        Test 500 error handling.

        Asserts:
            The response status code is 500.
            The response data contains 'Internal Server Error'.
        """
        @self.app.route('/error')
        def error_route():
            raise Exception("Test exception")

        response = self.client.get('/error')
        self.assertEqual(response.status_code, 500)
        self.assertIn(b'Internal Server Error', response.data)

    def test_database_connection_error(self):
        """Test database connection error handling"""
        with patch('src.core.db.Neo4jConnection.query') as mock_query:
            mock_query.side_effect = ServiceUnavailable("Database is unavailable")
            response = self.client.get('/optimize/calculate')
            self.assertEqual(response.status_code, 503)
            self.assertIn(b'Database service is unavailable', response.data)

    def test_database_auth_error(self):
        """Test database authentication error handling"""
        with patch('src.core.db.Neo4jConnection.query') as mock_query:
            mock_query.side_effect = AuthError("Invalid credentials")
            response = self.client.get('/optimize/calculate')
            self.assertEqual(response.status_code, 500)
            self.assertIn(b'Database authentication failed', response.data)

    def test_invalid_json_error(self):
        """Test invalid JSON handling in API endpoints"""
        response = self.client.post('/optimize/calculate', 
                                  data='invalid json',
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid JSON', response.data)

    def test_missing_required_field(self):
        """Test missing required field handling"""
        response = self.client.post('/optimize/calculate',
                                  json={},
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Missing required fields', response.data)

    def test_method_not_allowed(self):
        """Test method not allowed error handling"""
        response = self.client.post('/history/item/123')  # Assuming this is GET only
        self.assertEqual(response.status_code, 405)
        self.assertIn(b'Method Not Allowed', response.data)

    def test_rate_limit_exceeded(self):
        """Test rate limiting error handling"""
        # Make multiple requests quickly to trigger rate limit
        responses = [self.client.get('/optimize/calculate') for _ in range(50)]
        self.assertTrue(any(r.status_code == 429 for r in responses))
        self.assertTrue(any(b'Too Many Requests' in r.data for r in responses))

    def test_invalid_item_id(self):
        """Test invalid item ID error handling"""
        response = self.client.get('/history/item/invalid_id')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Item not found', response.data)

    @patch('src.core.db.Neo4jConnection')
    def test_database_timeout(self, mock_db):
        """Test database timeout handling"""
        mock_db.query.side_effect = Exception("Operation timed out")
        response = self.client.get('/optimize/calculate')
        self.assertEqual(response.status_code, 504)
        self.assertIn(b'Request timed out', response.data)

if __name__ == '__main__':
    unittest.main()
