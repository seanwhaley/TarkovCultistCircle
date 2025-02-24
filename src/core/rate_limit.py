"""Memory-based rate limiting for Flask applications."""
from datetime import datetime
import logging
from typing import Dict, Optional, Tuple, Union
from flask import request, current_app
from functools import wraps

logger = logging.getLogger(__name__)

class MemoryRateLimiter:
    """Rate limiting implementation using in-memory storage."""
    _storage = {}
    
    @classmethod
    def check_rate_limit(cls, key: str, limit: int, window: int) -> Tuple[bool, int]:
        now = datetime.now().timestamp()
        bucket = cls._storage.get(key, {"timestamps": [], "window_start": now})
        
        # Clean old entries
        bucket["timestamps"] = [ts for ts in bucket["timestamps"] if ts > now - window]
        
        if len(bucket["timestamps"]) >= limit:
            return False, len(bucket["timestamps"])
            
        bucket["timestamps"].append(now)
        cls._storage[key] = bucket
        return True, len(bucket["timestamps"])

def rate_limit(limits: Dict[str, Tuple[int, int]]):
    """
    Rate limiting decorator for Flask routes.
    
    Args:
        limits: Dictionary of rate limits. Key is the limit name,
               value is tuple of (number of requests, window in seconds)
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            for limit_name, (limit, window) in limits.items():
                key = f"{request.remote_addr}:{limit_name}"
                allowed, current = MemoryRateLimiter.check_rate_limit(key, limit, window)
                
                if not allowed:
                    return {
                        "error": "Rate limit exceeded",
                        "limit": limit,
                        "current": current,
                        "window": window
                    }, 429
            
            return f(*args, **kwargs)
        return wrapped
    return decorator