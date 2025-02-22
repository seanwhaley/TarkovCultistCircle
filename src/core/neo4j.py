from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from flask import current_app
from neo4j import GraphDatabase, BasicAuth, Transaction, Session
from neo4j.exceptions import ServiceUnavailable, AuthError
from types import TracebackType
from uuid import uuid4
from src.config.settings import Settings
from src.database.protocols import DatabaseSession, DatabaseTransaction
from src.services.exceptions import DatabaseError

logger = logging.getLogger(__name__)

class Neo4jTransaction(DatabaseTransaction):
    def __init__(self, transaction: Transaction) -> None:
        self._transaction = transaction

    def __enter__(self) -> 'Neo4jTransaction':
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()

    def run(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        result = self._transaction.run(query, parameters or {})
        return [dict(record) for record in result]

    def commit(self) -> None:
        self._transaction.commit()

    def rollback(self) -> None:
        self._transaction.rollback()

class Neo4jSession(DatabaseSession):
    def __init__(self, session: Session) -> None:
        self._session = session

    def __enter__(self) -> 'Neo4jSession':
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[type[BaseException]],
        exc_tb: Optional[TracebackType]
    ) -> None:
        self.close()

    def run(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        result = self._session.run(query, parameters or {})
        return [dict(record) for record in result]

    def begin_transaction(self) -> Neo4jTransaction:
        return Neo4jTransaction(self._session.begin_transaction())

    def close(self) -> None:
        self._session.close()

class Neo4jDB:
    def __init__(self) -> None:
        config = Settings()
        try:
            self._driver = GraphDatabase.driver(
                config.neo4j_uri,
                auth=(config.neo4j_user, config.neo4j_password)
            )
            self.verify_connection()
        except (ServiceUnavailable, AuthError) as e:
            raise DatabaseError(f"Failed to connect to Neo4j: {str(e)}")

    def verify_connection(self) -> bool:
        """Verify database connection."""
        try:
            with self.session() as session:
                result = session.run("RETURN 1")
                return bool(result[0][0] == 1)
        except Exception as e:
            raise DatabaseError(f"Database connection verification failed: {str(e)}")

    def session(self) -> Neo4jSession:
        """Get a new database session."""
        return Neo4jSession(self._driver.session())

    def close(self) -> None:
        """Close all database connections."""
        if hasattr(self, '_driver'):
            self._driver.close()

    def __enter__(self) -> 'Neo4jDB':
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[type[BaseException]],
        exc_tb: Optional[TracebackType]
    ) -> None:
        self.close()

class Neo4jClient:
    """Neo4j client with basic authentication."""
    
    def __init__(self):
        self.driver = self.get_driver()

    @staticmethod
    def get_auth() -> BasicAuth:
        return BasicAuth(
            current_app.config['NEO4J_USER'],
            current_app.config['NEO4J_PASSWORD']
        )

    @classmethod
    def get_driver(cls):
        auth = cls.get_auth()
        return GraphDatabase.driver(
            current_app.config['NEO4J_URI'],
            auth=auth,
            max_connection_pool_size=current_app.config['NEO4J_MAX_CONNECTION_POOL_SIZE']
        )

    def close(self):
        self.driver.close()

    def find_optimal_combinations(self, min_total: float = 400000, max_items: int = 5) -> List[Dict[str, Any]]:
        """Find optimal item combinations based on criteria."""
        with self.driver.session() as session:
            query = """
            MATCH (i:Item)
            WHERE (i.blacklisted IS NULL OR i.blacklisted = false OR 
                   i.blacklistExpires < datetime())
            WITH i, 
                 CASE 
                    WHEN i.priceOverride IS NOT NULL 
                         AND (i.priceOverrideExpires IS NULL OR i.priceOverrideExpires > datetime())
                    THEN i.priceOverride 
                    ELSE i.basePrice 
                 END as effectivePrice
            WITH collect({
                item: i,
                price: effectivePrice
            }) as items
            CALL {
                WITH items
                UNWIND range(1, $max_items) as len
                WITH items, len
                CALL apoc.coll.combinations(items, len) YIELD value
                WITH value, 
                     reduce(total = 0, x IN value | total + x.price) as totalPrice
                WHERE totalPrice >= $min_total
                RETURN value, totalPrice
                ORDER BY totalPrice ASC
                LIMIT 10
            }
            RETURN [x IN value | x.item {.*, effectivePrice: x.price}] as items,
                   totalPrice
            """
            
            result = session.run(
                query,
                min_total=min_total,
                max_items=max_items
            )
            return [record.data() for record in result]

    def save_combination(self, items: List[str], total_price: float) -> str:
        """Save a combination with UUID for future reference."""
        combination_id = str(uuid4())
        with self.driver.session() as session:
            query = """
            CREATE (c:Combination {
                id: $id,
                created: datetime(),
                totalPrice: $total_price
            })
            WITH c
            UNWIND $items as item_id
            MATCH (i:Item {id: item_id})
            CREATE (c)-[:INCLUDES]->(i)
            RETURN c.id
            """
            session.run(query, id=combination_id, items=items, total_price=total_price)
            return combination_id

    def get_combination_history(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Get paginated combination history with items."""
        with self.driver.session() as session:
            query = """
            MATCH (c:Combination)
            WITH c
            ORDER BY c.created DESC
            SKIP $skip
            LIMIT $limit
            MATCH (c)-[:INCLUDES]->(i:Item)
            WITH c, collect({
                id: i.id,
                name: i.name,
                basePrice: i.basePrice,
                priceOverride: i.priceOverride
            }) as items
            RETURN {
                id: c.id,
                created: c.created,
                totalPrice: c.totalPrice,
                items: items
            } as combination
            """
            
            count_query = """
            MATCH (c:Combination)
            RETURN count(c) as total
            """
            
            results = session.run(query, skip=(page-1)*per_page, limit=per_page)
            combinations = [record['combination'] for record in results]
            
            count_result = session.run(count_query)
            total = count_result.single()['total']
            
            return {
                'combinations': combinations,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }

    def delete_combination(self, combination_id: str) -> None:
        """Delete a combination and its relationships."""
        with self.driver.session() as session:
            query = """
            MATCH (c:Combination {id: $id})
            DETACH DELETE c
            """
            session.run(query, id=combination_id)

    def set_price_override(self, item_id: str, price: float, duration: Optional[int] = None) -> None:
        """Set a price override for an item."""
        expires = None if duration is None else datetime.now(datetime.timezone.utc) + timedelta(minutes=duration)
        
        with self.driver.session() as session:
            query = """
            MATCH (i:Item {id: $item_id})
            SET i.priceOverride = $price,
                i.priceOverrideExpires = $expires
            """
            session.run(query, item_id=item_id, price=price, expires=expires)

    def set_blacklist(self, item_id: str, blacklisted: bool, duration: Optional[int] = None) -> None:
        """Blacklist or unblacklist an item."""
        expires = None if duration is None else datetime.utcnow() + timedelta(minutes=duration)
        
        with self.driver.session() as session:
            query = """
            MATCH (i:Item {id: $item_id})
            SET i.blacklisted = $blacklisted,
                i.blacklistExpires = $expires
            """
            session.run(query, item_id=item_id, blacklisted=blacklisted, expires=expires)

    def set_lock(self, item_id: str, locked: bool, duration: Optional[int] = None) -> None:
        """Lock or unlock an item."""
        expires = None if duration is None else datetime.utcnow() + timedelta(minutes=duration)
        
        with self.driver.session() as session:
            query = """
            MATCH (i:Item {id: $item_id})
            SET i.locked = $locked,
                i.lockExpires = $expires
            """
            session.run(query, item_id=item_id, locked=locked, expires=expires)

    def upsert_item(self, item_data: Dict[str, Any]) -> None:
        """Create or update an item in the database."""
        with self.driver.session() as session:
            query = """
            MERGE (i:Item {id: $id})
            SET i += {
                name: $name,
                basePrice: $basePrice,
                fleaMarketFee: $fleaMarketFee,
                weight: $weight,
                updated: $updated
            }
            """
            session.run(query, **item_data)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
