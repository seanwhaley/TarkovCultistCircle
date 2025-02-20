import unittest
from src.application.app_factory import ApplicationFactory

class ErrorHandlingTestCase(unittest.TestCase):
    """
    Test case for Flask application error handling.
    """
    def setUp(self):
        """
        Set up the test client.
        """
        self.app = ApplicationFactory.create_app()
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

if __name__ == '__main__':
    unittest.main()
