"""Unified in-memory caching functionality."""
import functools
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Callable, TypeVar, List
from collections import OrderedDict
import re
from flask import current_app
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class Cache:
    """LRU cache implementation with pattern-based invalidation."""
    
    def __init__(self, capacity: int = 1000):
        self._cache: OrderedDict[str, tuple[Any, datetime]] = OrderedDict()
        self.capacity = capacity
        self._cleanup_counter = 0
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key not in self._cache:
            return None
            
        value, expires_at = self._cache[key]
        if expires_at and datetime.utcnow() > expires_at:
            del self._cache[key]
            return None
            
        self._cache.move_to_end(key)
        return value
        
    def set(self, key: str, value: Any, timeout: int = 300) -> None:
        """Set value in cache with expiration."""
        expires_at = datetime.utcnow() + timedelta(seconds=timeout)
        
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = (value, expires_at)
        
        if len(self._cache) > self.capacity:
            self._cache.popitem(last=False)
            
        # Periodic cleanup
        self._cleanup_counter += 1
        if self._cleanup_counter >= 100:
            self._cleanup()
            self._cleanup_counter = 0
            
    def delete(self, key: str) -> None:
        """Remove specific key from cache."""
        self._cache.pop(key, None)
        
    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()
        
    def invalidate(self, pattern: str) -> None:
        """Invalidate all keys matching pattern."""
        regex = re.compile(pattern)
        keys_to_delete = [
            key for key in self._cache.keys()
            if regex.match(key)
        ]
        for key in keys_to_delete:
            del self._cache[key]
            
    def _cleanup(self) -> None:
        """Remove expired entries."""
        now = datetime.utcnow()
        expired = [
            k for k, (_, exp) in self._cache.items()
            if exp and exp < now
        ]
        for k in expired:
            del self._cache[k]

# Global cache instance
cache = Cache()

def cached(timeout_seconds: Optional[int] = 300):
    """Cache decorator for functions."""
    def decorator(f: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs) -> T:
            # Don't cache in testing/debug
            if current_app.config.get('TESTING') or current_app.config.get('DEBUG'):
                return f(*args, **kwargs)
                
            # Create cache key from function name and arguments
            key = f"{f.__module__}.{f.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                logger.debug(f"Cache hit: {key}")
                return result
            
            # Cache miss - call function and store result
            result = f(*args, **kwargs)
            if timeout_seconds is not None:
                cache.set(key, result, timeout_seconds)
                logger.debug(f"Cache miss - stored: {key}")
            return result
            
        return decorated_function
    return decorator

def invalidate_cache(pattern: Optional[str] = None) -> None:
    """Invalidate cached values matching pattern."""
    if pattern:
        cache.invalidate(pattern)
    else:
        cache.clear()
    logger.info(f"Cache invalidated with pattern: {pattern or 'all'}")

__all__ = ['cache', 'cached', 'invalidate_cache']