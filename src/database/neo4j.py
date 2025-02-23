"""Neo4j database interface with simplified implementation."""
from typing import Dict, Any, Optional, List
from neo4j import GraphDatabase, Driver, Session
import logging
from contextlib import contextmanager

from src.config import Config

logger = logging.getLogger(__name__)

class Neo4jDB:
    """Simplified Neo4j database handler."""
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
            raise
    
    @contextmanager
    def session(self) -> Session:
        """Get a database session."""
        if not self._driver:
            raise RuntimeError("Database not initialized")
            
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
            result = session.run(query, parameters or {})
            return [dict(record) for record in result]
    
    def execute(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> None:
        """Execute a write query."""
        with self.session() as session:
            session.run(query, parameters or {})
    
    def close(self) -> None:
        """Close the database connection."""
        if self._driver:
            self._driver.close()
            self._driver = None

# Global instance
db = Neo4jDB()
