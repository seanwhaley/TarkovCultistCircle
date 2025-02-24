"""Simple in-memory rate limiting implementation."""
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Tuple, Callable
from flask import request, current_app
import logging

logger = logging.getLogger(__name__)

class InMemoryRateLimiter:
    """Simple in-memory rate limiter using IP addresses as keys."""
    
    def __init__(self):
        self._requests: Dict[str, list] = defaultdict(list)
        self._cleanup_frequency = 100  # Cleanup every 100 requests
        self._request_count = 0
    
    def is_rate_limited(self, ip: str, limit: int, window: int) -> bool:
        """Check if requests from IP exceed limit within time window."""
        now = datetime.now()
        self._request_count += 1
        
        # Periodic cleanup of old entries
        if self._request_count >= self._cleanup_frequency:
            self._cleanup()
            self._request_count = 0
        
        # Remove old requests outside the window
        window_start = now - timedelta(seconds=window)
        self._requests[ip] = [ts for ts in self._requests[ip] if ts > window_start]
        
        # Add current request
        self._requests[ip].append(now)
        
        # Check if limit is exceeded
        return len(self._requests[ip]) > limit
    
    def _cleanup(self) -> None:
        """Remove entries older than the largest window size."""
        now = datetime.now()
        max_window = timedelta(hours=1)  # Maximum window size
        
        for ip in list(self._requests.keys()):
            self._requests[ip] = [
                ts for ts in self._requests[ip] 
                if now - ts < max_window
            ]
            if not self._requests[ip]:
                del self._requests[ip]

# Global rate limiter instance
_rate_limiter = InMemoryRateLimiter()

def rate_limit(limits: Dict[str, Tuple[int, int]]) -> Callable:
    """Rate limiting decorator using in-memory storage.
    
    Args:
        limits: Dictionary mapping path prefixes to (limit, window) tuples
               where limit is max requests and window is time in seconds
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_app.config.get('RATE_LIMIT_ENABLED', True):
                return f(*args, **kwargs)
            
            ip = request.remote_addr
            path = request.path
            
            # Get limit for path or use default
            limit, window = limits.get('default', (1000, 3600))  # Default: 1000 per hour
            for prefix, (l, w) in limits.items():
                if prefix != 'default' and path.startswith(prefix):
                    limit, window = l, w
                    break
            
            if _rate_limiter.is_rate_limited(ip, limit, window):
                logger.warning(f"Rate limit exceeded for IP {ip} on path {path}")
                return {
                    'error': 'Rate limit exceeded',
                    'retry_after': window
                }, 429
            
            return f(*args, **kwargs)
        return wrapped
    return decorator
