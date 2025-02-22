"""Database access layer."""
from src.database.neo4j import Neo4jDB, get_db, close_db
from src.database.protocols import DatabaseSession, DatabaseResult
from src.database.exceptions import DatabaseError, ConnectionError, AuthenticationError

__all__ = [
    'Neo4jDB',
    'get_db',
    'close_db',
    'DatabaseSession',
    'DatabaseResult',
    'DatabaseError',
    'ConnectionError',
    'AuthenticationError'
]
