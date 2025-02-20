import unittest
from src.application.app_factory import ApplicationFactory

class RoutesTestCase(unittest.TestCase):
    """
    Test case for Flask application routes.
    """
    def setUp(self):
        """
        Set up the test client.
        """
        self.app = ApplicationFactory.create_app()
        self.client = self.app.test_client()

    def test_home_route(self):
        """
        Test home route.

        Asserts:
            The response status code is 200.
            The response data contains 'Home Page'.
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Home Page', response.data)

    def test_login_route(self):
        """
        Test the login route.

        Asserts:
            The response status code is 200.
            The response data contains 'Login Page'.
        """
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login Page', response.data)

    def test_logout_route(self):
        """
        Test the logout route.

        Asserts:
            The response status code is 200.
            The response data contains 'Logout Page'.
        """
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logout Page', response.data)

    def test_items_index_route(self):
        """
        Test the items index route.

        Asserts:
            The response status code is 200.
            The response data contains the items main page.
        """
        response = self.client.get('/items/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Items Main Page', response.data)

    def test_list_items_route(self):
        """
        Test the list items route.

        Asserts:
            The response status code is 200.
            The response data contains the list of items.
        """
        response = self.client.get('/items/api/list')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'items', response.data)

if __name__ == '__main__':
    unittest.main()
