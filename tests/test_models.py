import unittest
from datetime import datetime
from src.application.models import Item
from src.models.base import BaseModel, Response, Neo4jModel
from src.application.app_factory import ApplicationFactory
from src.models import User
from src.models import PriceHistory
from src.models.item import MarketData
from src.core.database import Neo4jDB

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

class TestBaseModel(unittest.TestCase):
    def test_base_model_creation(self):
        model = BaseModel(id='test_id')
        self.assertEqual(model.id, 'test_id')
        self.assertIsInstance(model.created_at, datetime)
        self.assertIsInstance(model.updated_at, datetime)

    def test_base_model_to_dict(self):
        model = BaseModel(id='test_id')
        data = model.to_dict()
        self.assertEqual(data['id'], 'test_id')
        self.assertIn('created_at', data)
        self.assertIn('updated_at', data)

    def test_base_model_from_dict(self):
        now = datetime.utcnow()
        data = {
            'id': 'test_id',
            'created_at': now.isoformat(),
            'updated_at': now.isoformat()
        }
        model = BaseModel.from_dict(data)
        self.assertEqual(model.id, 'test_id')
        self.assertEqual(model.created_at.isoformat(), now.isoformat())
        self.assertEqual(model.updated_at.isoformat(), now.isoformat())

class TestResponse(unittest.TestCase):
    def test_response_creation(self):
        response = Response[str](data="test_data")
        self.assertEqual(response.data, "test_data")
        self.assertIsNone(response.error)
        self.assertTrue(response.success)

    def test_response_with_error(self):
        response = Response[str](error="test_error", success=False)
        self.assertIsNone(response.data)
        self.assertEqual(response.error, "test_error")
        self.assertFalse(response.success)

    def test_response_to_dict(self):
        response = Response[str](data="test_data", error="test_error", success=True)
        data = response.to_dict()
        self.assertEqual(data['data'], "test_data")
        self.assertEqual(data['error'], "test_error")
        self.assertTrue(data['success'])

class TestItem(unittest.TestCase):
    def test_item_creation(self):
        data = {
            'id': 'test_id',
            'name': 'Test Item',
            'basePrice': 1000,
            'lastLowPrice': 900,
            'avg24hPrice': 950,
            'updated': '2024-02-17T12:00:00'
        }
        item = Item(data)
        self.assertEqual(item.id, 'test_id')
        self.assertEqual(item.name, 'Test Item')
        self.assertEqual(item.base_price, 1000)
        self.assertEqual(item.last_low_price, 900)
        self.assertEqual(item.avg_24h_price, 950)
        self.assertEqual(item.updated, '2024-02-17T12:00:00')

    def test_item_to_dict(self):
        data = {
            'id': 'test_id',
            'name': 'Test Item',
            'basePrice': 1000,
            'lastLowPrice': 900,
            'avg24hPrice': 950,
            'updated': '2024-02-17T12:00:00'
        }
        item = Item(data)
        item_dict = item.to_dict()
        self.assertEqual(item_dict['id'], 'test_id')
        self.assertEqual(item_dict['name'], 'Test Item')
        self.assertEqual(item_dict['basePrice'], 1000)
        self.assertEqual(item_dict['lastLowPrice'], 900)
        self.assertEqual(item_dict['avg24hPrice'], 950)
        self.assertEqual(item_dict['updated'], '2024-02-17T12:00:00')

    def test_item_from_neo4j_result(self):
        neo4j_data = {
            'properties': {
                'id': 'test_id',
                'name': 'Test Item',
                'basePrice': 1000,
                'lastLowPrice': 900,
                'avg24hPrice': 950,
                'updated': '2024-02-17T12:00:00'
            }
        }
        item = Item.from_neo4j_result(neo4j_data)
        self.assertEqual(item.id, 'test_id')
        self.assertEqual(item.name, 'Test Item')
        self.assertEqual(item.base_price, 1000)

class TestNeo4jModel(unittest.TestCase):
    def test_neo4j_model_from_dict(self):
        class TestModel(Neo4jModel):
            def __init__(self, id: str, name: str):
                self.id = id
                self.name = name

        data = {'id': 'test_id', 'name': 'Test Name'}
        model = TestModel.from_dict(data)
        self.assertEqual(model.id, 'test_id')
        self.assertEqual(model.name, 'Test Name')

    def test_neo4j_model_to_dict(self):
        class TestModel(Neo4jModel):
            def __init__(self, id: str, name: str):
                self.id = id
                self.name = name

        model = TestModel(id='test_id', name='Test Name')
        data = model.to_dict()
        self.assertEqual(data['id'], 'test_id')
        self.assertEqual(data['name'], 'Test Name')

    def test_neo4j_model_from_neo4j_result(self):
        class TestModel(Neo4jModel):
            def __init__(self, id: str, name: str):
                self.id = id
                self.name = name

        neo4j_data = {
            'properties': {
                'id': 'test_id',
                'name': 'Test Name'
            }
        }
        model = TestModel.from_neo4j_result(neo4j_data)
        self.assertEqual(model.id, 'test_id')
        self.assertEqual(model.name, 'Test Name')

if __name__ == '__main__':
    unittest.main()
