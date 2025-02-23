import unittest
import os
from unittest.mock import patch, MagicMock
from src.application.app_factory import ApplicationFactory
from src.application.extensions import ExtensionsManager
from src.core.extensions import init_extensions, limiter, login_manager
from src.config import Config

class TestAppConfiguration(unittest.TestCase):
    def setUp(self):
        self.app = ApplicationFactory.create_app(Config)
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        if self.app_context:
            self.app_context.pop()

    def test_config_loading(self):
        self.assertTrue(self.app.config['TESTING'])
        self.assertEqual(self.app.config['NEO4J_MAX_CONNECTION_POOL_SIZE'], 50)
        self.assertIsNotNone(self.app.config['SECRET_KEY'])

class TestExtensions(unittest.TestCase):
    def setUp(self):
        self.app = ApplicationFactory.create_app(Config)
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        if self.app_context:
            self.app_context.pop()

    def test_extensions_initialization(self):
        init_extensions(self.app)
        self.assertIsNotNone(limiter)
        self.assertIsNotNone(login_manager)

    def test_extensions_manager_singleton(self):
        manager1 = ExtensionsManager()
        manager2 = ExtensionsManager()
        self.assertIs(manager1, manager2)

    def test_database_connection(self):
        manager = ExtensionsManager()
        db = manager.get_db()
        self.assertIsNotNone(db)
        self.assertEqual(db.uri, self.app.config['NEO4J_URI'])

    @patch('src.core.db.Neo4jConnection')
    def test_database_reconnection(self, mock_db):
        # Simulate database disconnection and reconnection
        mock_db.return_value.query.side_effect = [
            Exception("Connection lost"),  # First call fails
            [{'result': 'success'}]  # Second call succeeds after reconnection
        ]
        
        manager = ExtensionsManager()
        db = manager.get_db()
        
        # First query fails
        with self.assertRaises(Exception):
            db.query("TEST QUERY")
        
        # Second query should succeed after automatic reconnection
        result = db.query("TEST QUERY")
        self.assertEqual(result[0]['result'], 'success')

    def test_login_manager_configuration(self):
        init_extensions(self.app)
        self.assertEqual(login_manager.login_view, 'auth.login')
        self.assertEqual(login_manager.session_protection, 'strong')

    def test_rate_limiter_configuration(self):
        init_extensions(self.app)
        # Test basic configuration
        self.assertEqual(self.app.config['RATELIMIT_STORAGE_URL'], 'memory://')
        self.assertEqual(self.app.config['RATELIMIT_STRATEGY'], 'fixed-window')
        
        # Test rate limit settings
        self.assertEqual(self.app.config['API_RATE_LIMIT'], 1000)
        self.assertEqual(self.app.config['API_REFRESH_LIMIT'], 20)

        # Test rate limiting is disabled in testing
        self.assertFalse(self.app.config.get('RATE_LIMIT_ENABLED', True))

if __name__ == '__main__':
    unittest.main()