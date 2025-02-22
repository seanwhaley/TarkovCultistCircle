"""Enhanced caching system using cachetools and Redis for FastAPI."""
from functools import wraps
from typing import Any, Callable, TypeVar, cast, Optional
from cachetools import TTLCache, keys
import structlog
import pickle
import logging

from fastapi import Request
from redis.asyncio import Redis

from src.core.logging import get_logger
from src.core.redis import RedisManager

logger = get_logger(__name__)
T = TypeVar("T")

# Main cache instance with 1000 items max and 5 minute TTL
CACHE = TTLCache(maxsize=1000, ttl=300)

def cached(
    timeout: int = 300,
    key_prefix: str = "",
    unless: Callable[..., bool] = None
) -> Callable:
    """Enhanced caching decorator with prefix support and conditional caching."""
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            if unless and unless(*args, **kwargs):
                return await func(*args, **kwargs)
                
            # Create cache key from function name, args, and kwargs
            cache_key = keys.hashkey(key_prefix, func.__name__, *args, **kwargs)
            
            try:
                result = CACHE.get(cache_key)
                if result is not None:
                    logger.debug("cache.hit", key=cache_key)
                    return cast(T, result)
                    
                logger.debug("cache.miss", key=cache_key)
                result = await func(*args, **kwargs)
                CACHE[cache_key] = result
                return result
                
            except Exception as e:
                logger.error("cache.error", 
                           error=str(e), 
                           key=cache_key,
                           exc_info=True)
                return await func(*args, **kwargs)
                
        return wrapper
    return decorator

def clear_cache() -> None:
    """Clear all cached items."""
    CACHE.clear()
    logger.info("cache.cleared")

def cache_key_builder(
    prefix: str,
    request: Request,
    *args: Any,
    **kwargs: Any
) -> str:
    """Build a cache key from request and arguments."""
    # Include query params and path in key
    key_parts = [
        prefix,
        request.url.path,
        str(request.query_params),
    ]
    
    # Include relevant arguments
    if args:
        key_parts.extend(str(arg) for arg in args)
    if kwargs:
        key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        
    # Generate hash for the key
    key = ":".join(key_parts)
    return hashlib.sha256(key.encode()).hexdigest()

def cache(
    *, 
    expire: int = 300,
    prefix: str = "cache:",
    key_builder: Optional[Callable] = None,
    include_user: bool = False
):
    """
    Cache decorator for FastAPI endpoint responses.
    
    Args:
        expire: Cache expiration time in seconds
        prefix: Cache key prefix
        key_builder: Custom function to build cache key
        include_user: Whether to include user ID in cache key
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            # Get request object from args
            request = next((arg for arg in args if isinstance(arg, Request)), None)
            if not request:
                return await func(*args, **kwargs)

            # Build cache key
            if key_builder:
                cache_key = key_builder(prefix, request, *args, **kwargs)
            else:
                cache_key = cache_key_builder(prefix, request, *args, **kwargs)
                
            # Add user ID to key if required
            if include_user and hasattr(request.state, "user_id"):
                cache_key = f"{cache_key}:user:{request.state.user_id}"

            try:
                # Get Redis client
                redis = await RedisManager.get_redis()
                
                # Try to get cached response
                cached = await redis.get(cache_key)
                if cached:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return json.loads(cached)
                
                # Generate new response
                response = await func(*args, **kwargs)
                
                # Cache the response
                try:
                    await redis.set(
                        cache_key,
                        json.dumps(response),
                        ex=expire
                    )
                    logger.debug(f"Cached response for key: {cache_key}")
                except (TypeError, ValueError) as e:
                    logger.error(f"Failed to cache response: {str(e)}")
                
                return response
                
            except Exception as e:
                logger.error(f"Cache error: {str(e)}")
                # On cache errors, just execute the function
                return await func(*args, **kwargs)
                
        return wrapper
    return decorator

async def invalidate_pattern(pattern: str = "*", prefix: str = "cache:") -> int:
    """
    Invalidate cache entries matching a pattern.
    
    Args:
        pattern: Pattern to match cache keys
        prefix: Cache key prefix
    
    Returns:
        Number of keys deleted
    """
    try:
        redis = await RedisManager.get_redis()
        keys = await redis.keys(f"{prefix}{pattern}")
        if keys:
            return await redis.delete(*keys)
        return 0
    except Exception as e:
        logger.error(f"Failed to invalidate cache pattern: {str(e)}")
        return 0

async def invalidate_key(key: str, prefix: str = "cache:") -> bool:
    """
    Invalidate a specific cache key.
    
    Args:
        key: Cache key to invalidate
        prefix: Cache key prefix
    
    Returns:
        True if key was deleted, False otherwise
    """
    try:
        redis = await RedisManager.get_redis()
        return bool(await redis.delete(f"{prefix}{key}"))
    except Exception as e:
        logger.error(f"Failed to invalidate cache key: {str(e)}")
        return False
