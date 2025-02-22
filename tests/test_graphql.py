from typing import Dict, Any, List, Generator
import pytest
from graphene.test import Client
from flask import Flask
from src.graphql.schema import schema
from src.core.db import Neo4jConnection
from src.application.app_factory import create_app
from src.config import Config
from src.application.models import Item

@pytest.fixture
def app() -> Flask:
    app = create_app(Config)
    app.config.update({
        'TESTING': True,
        'NEO4J_URI': 'bolt://localhost:7687',
        'NEO4J_USER': 'neo4j',
        'NEO4J_PASSWORD': 'test'
    })
    return app

@pytest.fixture
def db(app: Flask) -> Generator[Neo4jConnection, None, None]:
    db = Neo4jConnection(
        uri=app.config['NEO4J_URI'],
        user=app.config['NEO4J_USER'],
        password=app.config['NEO4J_PASSWORD'],
        database='neo4j'
    )
    # Clear test data
    db.query("MATCH (n) DETACH DELETE n")
    yield db
    # Cleanup after tests
    db.query("MATCH (n) DETACH DELETE n")
    db.close()

@pytest.fixture
def sample_items() -> List[Dict[str, Any]]:
    return [
        {
            "id": "item1",
            "name": "Test Item 1",
            "basePrice": 1000,
            "lastLowPrice": 900,
            "avg24hPrice": 950,
            "updated": "2024-02-17T12:00:00"
        },
        {
            "id": "item2",
            "name": "Test Item 2",
            "basePrice": 2000,
            "lastLowPrice": 1800,
            "avg24hPrice": 1900,
            "updated": "2024-02-17T12:00:00"
        }
    ]

def test_query_items(app: Flask, db: Neo4jConnection, sample_items: List[Dict[str, Any]]) -> None:
    client = Client(schema)
    
    # Setup test data
    for item in sample_items:
        db.query(
            """
            CREATE (i:Item {
                id: $id,
                name: $name,
                basePrice: $basePrice,
                lastLowPrice: $lastLowPrice,
                avg24hPrice: $avg24hPrice,
                updated: $updated
            })
            """,
            parameters=item
        )
    
    query = """
    query {
        items {
            id
            name
            basePrice
            lastLowPrice
            avg24hPrice
            updated
        }
    }
    """
    
    result = client.execute(query)
    assert "errors" not in result, f"GraphQL query failed: {result.get('errors')}"
    
    items = result["data"]["items"]
    assert len(items) == len(sample_items)
    for item, sample in zip(sorted(items, key=lambda x: x["id"]), 
                          sorted(sample_items, key=lambda x: x["id"])):
        assert item["id"] == sample["id"]
        assert item["basePrice"] == sample["basePrice"]
        assert item["lastLowPrice"] == sample["lastLowPrice"]
        assert item["avg24hPrice"] == sample["avg24hPrice"]

def test_mutation_update_price(app: Flask, db: Neo4jConnection, sample_items: List[Dict[str, Any]]) -> None:
    client = Client(schema)
    test_item = sample_items[0]
    new_price = 1500
    
    # Setup test data
    db.query(
        """
        CREATE (i:Item {
            id: $id,
            name: $name,
            basePrice: $basePrice,
            lastLowPrice: $lastLowPrice,
            avg24hPrice: $avg24hPrice,
            updated: $updated
        })
        """,
        parameters=test_item
    )
    
    mutation = """
    mutation UpdatePrice($itemId: ID!, $price: Int!) {
        updatePrice(input: {
            itemId: $itemId,
            price: $price
        }) {
            success
            message
            item {
                id
                basePrice
            }
        }
    }
    """
    
    variables = {
        "itemId": test_item["id"],
        "price": new_price
    }
    
    result = client.execute(mutation, variables=variables)
    assert "errors" not in result, f"GraphQL mutation failed: {result.get('errors')}"
    
    assert result["data"]["updatePrice"]["success"] is True
    assert result["data"]["updatePrice"]["item"]["basePrice"] == new_price

    # Verify database state
    db_result = db.query(
        "MATCH (i:Item {id: $id}) RETURN i.basePrice as price",
        parameters={"id": test_item["id"]}
    )
    assert db_result[0]["price"] == new_price

def test_query_item_by_id(app: Flask, db: Neo4jConnection, sample_items: List[Dict[str, Any]]) -> None:
    client = Client(schema)
    test_item = sample_items[0]
    
    # Setup test data
    db.query(
        """
        CREATE (i:Item {
            id: $id,
            name: $name,
            basePrice: $basePrice,
            lastLowPrice: $lastLowPrice,
            avg24hPrice: $avg24hPrice,
            updated: $updated
        })
        """,
        parameters=test_item
    )
    
    query = """
    query GetItem($id: ID!) {
        item(id: $id) {
            id
            name
            basePrice
            lastLowPrice
            avg24hPrice
            updated
        }
    }
    """
    
    variables = {"id": test_item["id"]}
    result = client.execute(query, variables=variables)
    assert "errors" not in result, f"GraphQL query failed: {result.get('errors')}"
    
    item = result["data"]["item"]
    assert item["id"] == test_item["id"]
    assert item["name"] == test_item["name"]
    assert item["basePrice"] == test_item["basePrice"]
    assert item["lastLowPrice"] == test_item["lastLowPrice"]
    assert item["avg24hPrice"] == test_item["avg24hPrice"]

def test_query_item_price_history(app: Flask, db: Neo4jConnection, sample_items: List[Dict[str, Any]]) -> None:
    client = Client(schema)
    test_item = sample_items[0]
    
    # Setup test data with price history
    db.query(
        """
        CREATE (i:Item {
            id: $id,
            name: $name,
            basePrice: $basePrice,
            lastLowPrice: $lastLowPrice,
            avg24hPrice: $avg24hPrice,
            updated: $updated
        })
        WITH i
        UNWIND [
            {price: 1000, timestamp: '2024-02-15T12:00:00'},
            {price: 1100, timestamp: '2024-02-16T12:00:00'},
            {price: 1200, timestamp: '2024-02-17T12:00:00'}
        ] as history
        CREATE (p:PricePoint {price: history.price, timestamp: history.timestamp})
        CREATE (i)-[:HAS_PRICE_HISTORY]->(p)
        """,
        parameters=test_item
    )
    
    query = """
    query GetItemPriceHistory($id: ID!) {
        itemPriceHistory(id: $id) {
            price
            timestamp
        }
    }
    """
    
    variables = {"id": test_item["id"]}
    result = client.execute(query, variables=variables)
    assert "errors" not in result, f"GraphQL query failed: {result.get('errors')}"
    
    history = result["data"]["itemPriceHistory"]
    assert len(history) == 3
    assert all(p["price"] > 0 for p in history)
    assert all("timestamp" in p for p in history)
