"""Neo4j database interface."""

from typing import List, Dict, Any, Optional, Union, TypeVar, Callable, Protocol
from neo4j import GraphDatabase, Session, Transaction, Result
from src.config.settings import Settings

T = TypeVar('T')

class TransactionWork(Protocol):
    def __call__(self, tx: Transaction, *args: Any, **kwargs: Any) -> Any: ...

class Neo4jDB:
    def __init__(self) -> None:
        config = Settings()
        self._driver = GraphDatabase.driver(
            config.neo4j_uri,
            auth=(config.neo4j_user, config.neo4j_password)
        )

    def close(self) -> None:
        """Close the database connection."""
        self._driver.close()

    def query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a Cypher query and return results."""
        with self._driver.session() as session:
            result = session.run(query, parameters or {})
            return [dict(record) for record in result]

    def write_transaction(
        self,
        work: TransactionWork,
        *args: Any,
        **kwargs: Any
    ) -> Any:
        """Execute a write transaction."""
        with self._driver.session() as session:
            return session.write_transaction(work, *args, **kwargs)

    def read_transaction(
        self,
        work: TransactionWork,
        *args: Any,
        **kwargs: Any
    ) -> Any:
        """Execute a read transaction."""
        with self._driver.session() as session:
            return session.read_transaction(work, *args, **kwargs)

    def create_constraints(self) -> None:
        """Create database constraints."""
        constraints = [
            "CREATE CONSTRAINT item_id_unique IF NOT EXISTS FOR (i:Item) REQUIRE i.id IS UNIQUE",
            "CREATE CONSTRAINT vendor_name_unique IF NOT EXISTS FOR (v:Vendor) REQUIRE v.name IS UNIQUE",
            "CREATE CONSTRAINT category_id_unique IF NOT EXISTS FOR (c:Category) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT task_id_unique IF NOT EXISTS FOR (t:Task) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT trade_id_unique IF NOT EXISTS FOR (t:Trade) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT item_required_props IF NOT EXISTS FOR (i:Item) REQUIRE i.id IS NOT NULL",
            "CREATE CONSTRAINT item_name_exists IF NOT EXISTS FOR (i:Item) REQUIRE i.name IS NOT NULL",
            "CREATE CONSTRAINT vendor_name_exists IF NOT EXISTS FOR (v:Vendor) REQUIRE v.name IS NOT NULL"
        ]
        
        with self._driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                except Exception as e:
                    # Log the error but continue with other constraints
                    print(f"Error creating constraint: {e}")

    def create_indexes(self) -> None:
        """Create database indexes."""
        indexes = [
            "CREATE INDEX item_name IF NOT EXISTS FOR (i:Item) ON (i.name)",
            "CREATE INDEX vendor_name IF NOT EXISTS FOR (v:Vendor) ON (v.name)",
            "CREATE INDEX category_id IF NOT EXISTS FOR (c:Category) ON (c.id)",
            "CREATE INDEX task_id IF NOT EXISTS FOR (t:Task) ON (t.id)",
            "CREATE INDEX station_name IF NOT EXISTS FOR (s:Station) ON (s.name)",
            "CREATE INDEX trade_id IF NOT EXISTS FOR (t:Trade) ON (t.id)",
            "CREATE INDEX item_price_idx IF NOT EXISTS FOR (i:Item) ON (i.basePrice, i.lastLowPrice)",
            "CREATE INDEX trade_type_level IF NOT EXISTS FOR (t:Trade) ON (t.type, t.level)"
        ]
        
        with self._driver.session() as session:
            for index in indexes:
                try:
                    session.run(index)
                except Exception as e:
                    # Log the error but continue with other indexes
                    print(f"Error creating index: {e}")

    def ensure_connection(self) -> bool:
        """Test database connection and setup."""
        try:
            with self._driver.session() as session:
                result = session.run("RETURN 1")
                return bool(result.single())
        except Exception:
            return False