from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
import logging

from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from neo4j.exceptions import ServiceUnavailable

from src.core.config import Settings
from src.core.exceptions import DatabaseError

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Async Neo4j database manager with connection pooling."""
    
    _instance: Optional['DatabaseManager'] = None
    _driver: Optional[AsyncDriver] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def initialize(cls, settings: Settings) -> None:
        """Initialize database connection pool."""
        if cls._driver is None:
            try:
                cls._driver = AsyncGraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                    max_connection_pool_size=settings.NEO4J_MAX_POOL_SIZE
                )
                # Verify connectivity
                await cls._driver.verify_connectivity()
                logger.info("Successfully connected to Neo4j database")
            except ServiceUnavailable as e:
                logger.error(f"Failed to connect to Neo4j: {str(e)}")
                raise DatabaseError("Database service is unavailable")
            except Exception as e:
                logger.error(f"Database initialization error: {str(e)}")
                raise DatabaseError(f"Failed to initialize database: {str(e)}")

    @classmethod
    async def close(cls) -> None:
        """Close all database connections."""
        if cls._driver:
            await cls._driver.close()
            cls._driver = None
            logger.info("Database connections closed")

    @classmethod
    @asynccontextmanager
    async def session(cls) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session."""
        if not cls._driver:
            raise DatabaseError("Database not initialized")
        
        session = None
        try:
            session = cls._driver.session()
            yield session
        except Exception as e:
            logger.error(f"Session error: {str(e)}")
            raise DatabaseError(f"Database session error: {str(e)}")
        finally:
            if session:
                await session.close()

    @classmethod
    @asynccontextmanager
    async def transaction(cls) -> AsyncGenerator[AsyncSession, None]:
        """Get a database transaction."""
        async with cls.session() as session:
            try:
                tx = await session.begin_transaction()
                yield tx
                await tx.commit()
            except Exception as e:
                await tx.rollback()
                logger.error(f"Transaction error: {str(e)}")
                raise DatabaseError(f"Database transaction error: {str(e)}")

    @classmethod
    async def health_check(cls) -> bool:
        """Check database connectivity."""
        if not cls._driver:
            return False
            
        try:
            await cls._driver.verify_connectivity()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False