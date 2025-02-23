from typing import Optional
import logging

from redis.asyncio import Redis, ConnectionPool
from src.core.config import Settings

logger = logging.getLogger(__name__)

class RedisManager:
    """Manager for Redis connections."""
    _pool: Optional[ConnectionPool] = None
    _redis: Optional[Redis] = None

    @classmethod
    async def initialize(cls, settings: Settings) -> None:
        """Initialize Redis connection pool."""
        if cls._pool is None:
            try:
                cls._pool = ConnectionPool.from_url(
                    settings.REDIS_URL,
                    max_connections=10,
                    decode_responses=True
                )
                # Test connection
                async with Redis(connection_pool=cls._pool) as redis:
                    await redis.ping()
                logger.info("Redis connection pool initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Redis connection pool: {e}")
                raise

    @classmethod
    async def get_redis(cls) -> Redis:
        """Get Redis client instance."""
        if cls._pool is None:
            raise RuntimeError("Redis connection pool not initialized")
        
        if cls._redis is None:
            cls._redis = Redis(connection_pool=cls._pool)
        
        return cls._redis

    @classmethod
    async def close(cls) -> None:
        """Close Redis connections."""
        if cls._redis:
            await cls._redis.close()
            cls._redis = None
        
        if cls._pool:
            await cls._pool.disconnect()
            cls._pool = None
            logger.info("Redis connections closed")