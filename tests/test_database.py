import unittest
from src.core.database import Neo4jDB
from src.models import Item  # Ensure this import is accurate

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Neo4jDB()
        self.db.initialize('bolt://localhost:7687', 'neo4j', 'password')
        self.session = self.db.get_session()

    def tearDown(self):
        self.session.close()
        self.db.close()

    def test_item_creation(self):
        with self.session as session:
            item = Item(uid='test_id', name='test_item', base_price=100.0)
            item.save()
            retrieved_item = Item.nodes.get(uid='test_id')
            self.assertEqual(retrieved_item.name, 'test_item')
            self.assertEqual(retrieved_item.base_price, 100.0)

if __name__ == '__main__':
    unittest.main()
