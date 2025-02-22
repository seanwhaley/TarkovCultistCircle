import unittest
import os
from unittest.mock import patch, MagicMock
from src.application.app_factory import ApplicationFactory
from src.application.extensions import ExtensionsManager
from src.core.extensions import init_extensions, cache, limiter, login_manager
from src.config import Config

class TestAppConfiguration(unittest.TestCase):
    def setUp(self):
        self.app = ApplicationFactory.create_app(Config)
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        if self.app_context:
            self.app_context.pop()

    def test_config_loading(self):
        self.assertTrue(self.app.config['TESTING'])
        self.assertEqual(self.app.config['NEO4J_MAX_CONNECTION_POOL_SIZE'], 50)
        self.assertIsNotNone(self.app.config['SECRET_KEY'])

    def test_environment_config(self):
        with patch.dict('os.environ', {
            'NEO4J_URI': 'bolt://testdb:7687',
            'NEO4J_USER': 'testuser',
            'NEO4J_PASSWORD': 'testpass',
            'NEO4J_MAX_POOL_SIZE': '100'
        }):
            app = ApplicationFactory.create_app(Config)
            self.assertEqual(app.config['NEO4J_URI'], 'bolt://testdb:7687')
            self.assertEqual(app.config['NEO4J_USER'], 'testuser')
            self.assertEqual(app.config['NEO4J_PASSWORD'], 'testpass')
            self.assertEqual(app.config['NEO4J_MAX_CONNECTION_POOL_SIZE'], 100)

    def test_blueprint_registration(self):
        # Test that all blueprints are registered
        blueprints = [
            'optimizer',
            'auth',
            'history',
            'market',
            'api',
            'errors'
        ]
        for blueprint in blueprints:
            self.assertIn(blueprint, self.app.blueprints)

    def test_static_files(self):
        client = self.app.test_client()
        response = client.get('/static/css/main.css')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'text/css; charset=utf-8')

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
        self.assertIsNotNone(cache)
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
        self.assertTrue(login_manager.session_protection == 'strong')

    def test_cache_configuration(self):
        init_extensions(self.app)
        # Test cache operations
        cache.set('test_key', 'test_value')
        self.assertEqual(cache.get('test_key'), 'test_value')

    def test_rate_limiter_configuration(self):
        init_extensions(self.app)
        # Test rate limiter
        self.assertTrue(limiter.enabled)
        self.assertEqual(limiter.default_limits, ["200 per day", "50 per hour"])

if __name__ == '__main__':
    unittest.main()