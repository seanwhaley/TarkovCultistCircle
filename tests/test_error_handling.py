"""Tests for error handling."""
import unittest
from unittest.mock import patch
from src.application.app_factory import ApplicationFactory
from src.config import Config
from src.database.exceptions import ConnectionError, QueryError, ValidationError

class ErrorHandlingTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.app = ApplicationFactory.create_app(Config)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_404_error(self):
        """Test not found error handling."""
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
        
        # Test JSON response
        response = self.client.get('/nonexistent', headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Not found')

    def test_database_connection_error(self):
        """Test database connection error handling."""
        with patch('src.database.neo4j.Neo4jDB._init_driver') as mock_init:
            mock_init.side_effect = ConnectionError("Failed to connect to database")
            response = self.client.get('/items')
            self.assertEqual(response.status_code, 503)
            
            # Test JSON response
            response = self.client.get('/items', headers={'Accept': 'application/json'})
            self.assertEqual(response.status_code, 503)
            self.assertIn('Service unavailable', response.json['error'])

    def test_database_query_error(self):
        """Test database query error handling."""
        with patch('src.database.neo4j.Neo4jDB.query') as mock_query:
            mock_query.side_effect = QueryError("Query execution failed")
            response = self.client.get('/items')
            self.assertEqual(response.status_code, 500)
            
            # Test JSON response
            response = self.client.get('/items', headers={'Accept': 'application/json'})
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json['error'], 'Database error')

    def test_validation_error(self):
        """Test validation error handling."""
        with patch('src.database.neo4j.Neo4jDB.execute') as mock_execute:
            mock_execute.side_effect = ValidationError("Invalid data format", {"field": "price"})
            response = self.client.post('/items', json={"invalid": "data"})
            self.assertEqual(response.status_code, 400)
            
            # Test JSON response
            response = self.client.post('/items', json={"invalid": "data"}, 
                                      headers={'Accept': 'application/json'})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json['error'], 'Validation error')
            self.assertIn('details', response.json)

if __name__ == '__main__':
    unittest.main()
