import unittest
import json
from src.application.app_factory import ApplicationFactory
from src.config import Config

class RoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = ApplicationFactory.create_app(Config)
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        if self.app_context:
            self.app_context.pop()

    # Auth Blueprint Tests
    def test_login_route(self):
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)

    def test_login_post(self):
        data = {
            'username': 'testuser',
            'password': 'testpass'
        }
        response = self.client.post('/auth/login', json=data)
        self.assertEqual(response.status_code, 200)

    def test_logout_route(self):
        response = self.client.get('/auth/logout')
        self.assertEqual(response.status_code, 200)

    # Optimizer Blueprint Tests
    def test_optimizer_index(self):
        response = self.client.get('/optimize/')
        self.assertEqual(response.status_code, 200)

    def test_optimizer_calculate(self):
        data = {
            'items': ['item1', 'item2'],
            'budget': 100000
        }
        response = self.client.post('/optimize/calculate', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('result', json.loads(response.data))

    # History Blueprint Tests
    def test_history_index(self):
        response = self.client.get('/history/')
        self.assertEqual(response.status_code, 200)

    def test_history_item(self):
        response = self.client.get('/history/item/test_id')
        self.assertEqual(response.status_code, 200)

    def test_history_market(self):
        response = self.client.get('/history/market')
        self.assertEqual(response.status_code, 200)

    def test_history_export(self):
        response = self.client.get('/history/export')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Content-Type', response.headers)
        self.assertEqual(response.headers['Content-Type'], 'application/json')

    # Error Routes Tests
    def test_404_error(self):
        response = self.client.get('/nonexistent-route')
        self.assertEqual(response.status_code, 404)

    def test_unauthorized_access(self):
        # Test accessing protected route without authentication
        response = self.client.get('/history/admin')
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
