"""Database initialization and connection management."""
import logging
from typing import Optional
from neo4j import GraphDatabase, Driver
from flask import current_app

logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Base database error."""
    pass

class Database:
    """Neo4j database connection manager."""
    _instance: Optional[Driver] = None

    @classmethod
    def get_driver(cls) -> Driver:
        """Get or create Neo4j driver instance."""
        if cls._instance is None:
            try:
                cls._instance = GraphDatabase.driver(
                    current_app.config['NEO4J_URI'],
                    auth=(
                        current_app.config['NEO4J_USER'],
                        current_app.config['NEO4J_PASSWORD']
                    ),
                    max_connection_pool_size=current_app.config.get('NEO4J_MAX_POOL_SIZE', 50)
                )
                # Verify connection
                cls._instance.verify_connectivity()
                logger.info("Successfully connected to Neo4j database")
            except Exception as e:
                logger.error(f"Failed to connect to Neo4j: {str(e)}")
                raise DatabaseError(f"Database connection failed: {str(e)}")
        return cls._instance

    @classmethod
    def close(cls) -> None:
        """Close database connection."""
        if cls._instance is not None:
            try:
                cls._instance.close()
                cls._instance = None
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {str(e)}")
                raise DatabaseError(f"Failed to close database connection: {str(e)}")

# Initialize database on first import
def init_db(app):
    """Initialize database with Flask app context."""
    with app.app_context():
        Database.get_driver()
        
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        Database.close()
