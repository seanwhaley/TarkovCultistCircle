# SAFE TO DELETE: Authentication tests consolidated into test_core.py
# Basic authentication functionality is now part of the core test suite

import unittest
from src.application.app_factory import ApplicationFactory
from src.auth.auth_service import AuthService
from src.models.user import User

class AuthTestCase(unittest.TestCase):
    """
    Test case for Flask application authentication and authorization.
    """
    def setUp(self):
        """
        Set up the test client.
        """
        self.app = ApplicationFactory.create_app()
        self.client = self.app.test_client()

    def test_login(self):
        """
        Test login functionality.

        Asserts:
            The response status code is 200.
            The response data contains 'Login Page'.
        """
        response = self.client.post('/login', data=dict(username='test', password='test'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login Page', response.data)

    def test_logout(self):
        """
        Test logout functionality.

        Asserts:
            The response status code is 200.
            The response data contains 'Logout Page'.
        """
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logout Page', response.data)

if __name__ == '__main__':
    unittest.main()
