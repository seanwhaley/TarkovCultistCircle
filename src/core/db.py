import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase
from dotenv import load_dotenv
import time

load_dotenv()

class Neo4jConnection:

    def __init__(self, uri, user, password, database):
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self.driver = None
        self.connect()

    def connect(self):
        max_retries = 5
        retry_delay = 5
        for attempt in range(max_retries):
            try:
                self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
                self.driver.verify_connectivity()
                print("Connected to Neo4j")
                return
            except Exception as e:
                print(f"Failed to connect to Neo4j (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        print("Failed to connect to Neo4j after multiple retries")

    def close(self):
        if self.driver is not None:
            self.driver.close()

    def query(self, query, parameters=None):
        max_retries = 3
        retry_delay = 2
        for attempt in range(max_retries):
            try:
                if self.driver is None:
                    print("No connection to Neo4j")
                    return []
                with self.driver.session(database=self.database) as session:
                    result = session.run(query, parameters)
                    return result.data()
            except Exception as e:
                print(f"Query failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        print("Query failed after multiple retries")
        return []

    def execute(self, query, parameters=None):
        max_retries = 3
        retry_delay = 2
        for attempt in range(max_retries):
            try:
                if self.driver is None:
                    print("No connection to Neo4j")
                    return
                with self.driver.session(database=self.database) as session:
                    session.run(query, parameters)
                return
            except Exception as e:
                print(f"Execute failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        print("Execute failed after multiple retries")

def get_db():
    uri = "bolt://neo4j_db:7687" # Construct the URI directly
    user = "neo4j" #os.environ.get('NEO4J_USER') # These are not used anymore
    password = "neo4j_password" #os.environ.get('NEO4J_PASSWORD') # These are not used anymore
    database = "neo4j" #os.environ.get('NEO4J_DATABASE')
    return Neo4jConnection(uri, user, password, database)

class Database:
    def __init__(self):
        self.connection = get_db()

    def save_items_to_db(self, items: List[Dict[str, Any]]) -> bool:
        try:
            for item in items:
                item_node = {
                    "id": item['id'],
                    "name": item['name'],
                    "basePrice": item['basePrice'],
                    "weight": item['weight'],
                    "updated": datetime.fromisoformat(item['updated'].replace('Z', '+00:00')),
                    "fleaMarketFee": item['fleaMarketFee']
                }
                self.connection.execute("""
                    MERGE (i:Item {id: $id})
                    SET i.name = $name, i.basePrice = $basePrice, i.weight = $weight, 
                        i.updated = $updated, i.fleaMarketFee = $fleaMarketFee
                """, item_node)
                
                for category in item['categories']:
                    self.connection.execute("""
                        MERGE (c:Category {name: $name})
                        MERGE (i:Item {id: $item_id})-[:BELONGS_TO]->(c)
                    """, {"name": category['name'], "item_id": item['id']})
                
                for buy in item['buyFor']:
                    self.connection.execute("""
                        MERGE (v:Vendor {name: $name})
                        MERGE (i:Item {id: $item_id})-[:BUYABLE_FROM {priceRUB: $priceRUB}]->(v)
                    """, {"name": buy['vendor']['name'], "item_id": item['id'], "priceRUB": buy['priceRUB']})
                
                for sell in item['sellFor']:
                    self.connection.execute("""
                        MERGE (v:Vendor {name: $name})
                        MERGE (i:Item {id: $item_id})-[:SELLS_TO {priceRUB: $priceRUB}]->(v)
                    """, {"name": sell['vendor']['name'], "item_id": item['id'], "priceRUB": sell['priceRUB']})
            return True
        except Exception as e:
            print(f"Error saving items: {str(e)}")
            return False

    def find_optimal_combination(self, min_price: int = 400000, max_items: int = 5):
        query = """
        MATCH (i:Item)
        WHERE NOT (i)-[:IS_BLACKLISTED]->(:BlacklistEntry {active: true})
        WITH i
        MATCH (i)-[b:BUYABLE_FROM]->(v:Vendor)
        WHERE NOT EXISTS(i.override_price)
        WITH i, MIN(b.priceRUB) as minBuyPrice
        ORDER BY minBuyPrice
        WITH COLLECT({item: i, buyPrice: minBuyPrice}) as items
        CALL apoc.algo.cover(items, max_items)
        YIELD cover
        WHERE REDUCE(s = 0, x IN cover | s + x.item.basePrice) >= min_price
        RETURN cover
        ORDER BY REDUCE(s = 0, x IN cover | s + x.buyPrice)
        LIMIT 1
        """
        result = self.connection.query(query, {"min_price": min_price, "max_items": max_items})
        return result