"""Neo4j database interface with relationship support."""
from typing import Dict, Any, Optional, List
from neo4j import GraphDatabase, Driver, Session
import logging
from contextlib import contextmanager
from uuid import uuid4
from datetime import datetime

from src.config import Config
from src.database.protocols import Neo4jSession, DatabaseResult
from src.database.exceptions import DatabaseError, ConnectionError, QueryError

logger = logging.getLogger(__name__)

class Neo4jDB:
    """Neo4j database handler with relationship management."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._driver: Optional[Driver] = None
        self._init_driver()
    
    def _init_driver(self) -> None:
        """Initialize the Neo4j driver.""" 
        if self._driver:
            return
            
        config = Config()
        try:
            self._driver = GraphDatabase.driver(
                config.NEO4J_URI,
                auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
            )
            self._driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise ConnectionError(f"Database connection failed: {str(e)}")
    
    @contextmanager
    def session(self) -> Session:
        """Get a database session."""
        if not self._driver:
            raise ConnectionError("Database not initialized")
            
        session = None
        try:
            session = self._driver.session()
            yield session
        finally:
            if session:
                session.close()

    def query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a read query."""
        with self.session() as session:
            try:
                result = session.run(query, parameters or {})
                return [dict(record) for record in result]
            except Exception as e:
                logger.error(f"Query error: {str(e)}")
                raise QueryError(f"Query execution failed: {str(e)}")

    def execute(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> None:
        """Execute a write query."""
        with self.session() as session:
            try:
                session.run(query, parameters or {})
            except Exception as e:
                logger.error(f"Execute error: {str(e)}")
                raise QueryError(f"Query execution failed: {str(e)}")

    def create_relationship(
        self,
        from_node_type: str,
        from_node_id: str,
        to_node_type: str,
        to_node_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """Create a relationship between nodes."""
        query = f"""
        MATCH (a:{from_node_type} {{uid: $from_id}})
        MATCH (b:{to_node_type} {{uid: $to_id}})
        CREATE (a)-[r:{relationship_type} $props]->(b)
        RETURN r
        """
        params = {
            "from_id": from_node_id,
            "to_id": to_node_id,
            "props": properties or {}
        }
        self.execute(query, params)

    def get_relationships(
        self,
        node_type: str,
        node_id: str,
        relationship_type: Optional[str] = None,
        direction: str = "OUTGOING"
    ) -> List[Dict[str, Any]]:
        """Get relationships for a node."""
        direction_symbol = "->" if direction == "OUTGOING" else "<-"
        rel_type = f":{relationship_type}" if relationship_type else ""
        
        query = f"""
        MATCH (n:{node_type} {{uid: $node_id}})
        {'MATCH (n)' + direction_symbol + f'[r{rel_type}]' + direction_symbol + '(m)'
         if relationship_type else
         f'MATCH (n)-[r]-{direction_symbol}(m)'}
        RETURN type(r) as type, r as properties, m as connected_node
        """
        return self.query(query, {"node_id": node_id})

    def close(self) -> None:
        """Close the database connection.""" 
        if self._driver:
            self._driver.close()
            self._driver = None

    def __enter__(self) -> 'Neo4jDB':
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

# Global instance
db = Neo4jDB()
