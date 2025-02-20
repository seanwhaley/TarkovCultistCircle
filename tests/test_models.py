import unittest
from src.application.app_factory import ApplicationFactory
from src.models import Item  # Ensure this import is accurate

class ModelsTestCase(unittest.TestCase):
    """
    Test case for Flask application models.
    """
    def setUp(self):
        """
        Set up the test client and database.
        """
        self.app = ApplicationFactory.create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        # Initialize the database (if applicable)
        # db.create_all()

    def tearDown(self):
        """
        Tear down the test client and database.
        """
        # Tear down the database (if applicable)
        # db.session.remove()
        # db.drop_all()
        self.app_context.pop()

    def test_model_creation(self):
        """
        Test model creation.

        Asserts:
            The model is created successfully.
        """
        model_instance = Item(name='Test Item', base_price=100.0)
        model_instance.save()
        self.assertIsNotNone(model_instance.uid)

class TestItemModel(unittest.TestCase):
    def test_item_creation(self):
        item = Item(uid='test_id', name='test_item', base_price=100.0)
        self.assertEqual(item.uid, 'test_id')
        self.assertEqual(item.name, 'test_item')
        self.assertEqual(item.base_price, 100.0)

if __name__ == '__main__':
    unittest.main()
