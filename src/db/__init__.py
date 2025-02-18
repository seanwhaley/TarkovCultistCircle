from neo4j import GraphDatabase
from flask import current_app, g
import os
import logging
from datetime import datetime, timezone
from src.models.graph_model import NodeLabels, RelationshipTypes, NodeProperties, validate_node, validate_relationship

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jDB:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        self.driver.close()
        
    def query(self, query, parameters=None):
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [record for record in result]
        except Exception as e:
            logger.error(f"Database query failed: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Parameters: {parameters}")
            raise

    def create_market_state(self, timestamp=None):
        query = """
        CREATE (ms:MarketState {
            timestamp: $timestamp,
            state: $state
        })
        RETURN ms
        """
        timestamp = timestamp or datetime.now(timezone.utc)
        return self.query(query, {
            'timestamp': timestamp.isoformat(),
            'state': 'normal'
        })

    def create_or_update_item(self, item):
        query = """
        // Create or update item node
        MERGE (i:Item {id: $id})
        ON CREATE SET 
            i.name = $name,
            i.base_price = toString($basePrice),
            i.updated = $updated,
            i.weight = $weight,
            i.short_name = $shortName,
            i.wiki_link = $wikiLink,
            i.flea_market_fee = toString($fleaMarketFee)
            
        // Create price history for each vendor
        WITH i
        UNWIND $buyFor as buy
        MERGE (v:Vendor {name: buy.vendor.name})
        ON CREATE SET v.min_level = buy.vendor.minTraderLevel
        CREATE (ph:PriceHistory {
            fetched_at: datetime(),
            price_rub: toString(buy.priceRUB),
            vendor_name: buy.vendor.name,
            currency: buy.currency,
            original_price: toString(buy.price)
        })
        CREATE (i)-[:HAD_PRICE]->(ph)
        CREATE (ph)-[:VENDOR_BOUGHT]->(v)
        
        // Create category relationships
        WITH i
        UNWIND $categories as cat
        MERGE (c:Category {name: cat.name})
        MERGE (i)-[:IN_CATEGORY]->(c)
        """
        
        try:
            # Transform data to match our model
            params = {
                'id': str(item['id']),
                'name': str(item['name']),
                'basePrice': item.get('basePrice', 0),
                'updated': item['updated'],
                'weight': float(item.get('weight', 0.0)),
                'shortName': item.get('shortName', ''),
                'wikiLink': item.get('wikiLink', ''),
                'fleaMarketFee': item.get('fleaMarketFee', 0),
                'buyFor': item.get('buyFor', []),
                'categories': item.get('categories', [])
            }

            # Validate against our model
            validation_issues = validate_node(NodeLabels.ITEM, {
                'id': params['id'],
                'name': params['name'],
                'base_price': str(params['basePrice']),
                'updated': params['updated']
            })

            if validation_issues:
                logger.error(f"Validation issues: {validation_issues}")
                return False

            self.query(query, params)
            return True

        except Exception as e:
            logger.error(f"Failed to create/update item {item.get('id')}: {str(e)}")
            return False

    def get_item_price_history(self, item_id, days=30):
        query = """
        MATCH (i:Item {id: $item_id})-[:HAD_PRICE]->(ph:PriceHistory)
        WHERE ph.fetched_at > datetime() - duration({days: $days})
        WITH ph, i
        OPTIONAL MATCH (ph)-[b:VENDOR_BOUGHT]->(v1:Vendor)
        OPTIONAL MATCH (ph)-[s:VENDOR_SOLD]->(v2:Vendor)
        RETURN i.name, 
               ph.fetched_at, 
               ph.game_updated_at,
               ph.base_price,
               collect(DISTINCT {vendor: v1.name, price: b.price_rub, type: 'buy'}) as buy_prices,
               collect(DISTINCT {vendor: v2.name, price: s.price_rub, type: 'sell'}) as sell_prices
        ORDER BY ph.fetched_at DESC
        """
        return self.query(query, {'item_id': item_id, 'days': days})

    def get_vendor_price_trends(self, vendor_name, days=30):
        query = """
        MATCH (v:Vendor {name: $vendor_name})
        MATCH (ph:PriceHistory)-[r:VENDOR_BOUGHT|VENDOR_SOLD]->(v)
        WHERE ph.fetched_at > datetime() - duration({days: $days})
        MATCH (i:Item)-[:HAD_PRICE]->(ph)
        RETURN i.name,
               ph.fetched_at,
               type(r) as transaction_type,
               r.price_rub as price
        ORDER BY ph.fetched_at DESC
        """
        return self.query(query, {'vendor_name': vendor_name, 'days': days})

def get_db():
    if 'db' not in g:
        uri = os.getenv('NEO4J_URI', 'bolt://neo4j_db:7687')
        user = os.getenv('NEO4J_USER', 'neo4j')
        password = os.getenv('NEO4J_PASSWORD')
        
        if not all([uri, user, password]):
            raise ValueError("Missing required Neo4j credentials")
            
        try:
            g.db = Neo4jDB(uri, user, password)
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
