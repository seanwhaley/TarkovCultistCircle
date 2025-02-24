"""Simple in-memory rate limiting middleware for Flask."""
from functools import wraps
import logging
from typing import Dict, Optional, Tuple, Callable
from flask import request, current_app
from werkzeug.wrappers import Response
from collections import defaultdict
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)

class RateLimiter:
    """Thread-safe in-memory rate limiter."""
    
    def __init__(self):
        self._requests = defaultdict(list)
        self._lock = threading.Lock()
        self._cleanup_counter = 0

    def is_rate_limited(self, key: str, limit: int, window: int) -> Tuple[bool, Dict[str, int]]:
        """Check if request should be rate limited."""
        now = datetime.utcnow()
        with self._lock:
            # Cleanup old entries periodically
            self._cleanup_counter += 1
            if self._cleanup_counter >= 100:
                self._cleanup()
                self._cleanup_counter = 0
            
            # Remove old requests outside window
            window_start = now - timedelta(seconds=window)
            self._requests[key] = [ts for ts in self._requests[key] if ts > window_start]
            
            # Add current request
            self._requests[key].append(now)
            
            # Get remaining requests
            count = len(self._requests[key])
            remaining = max(0, limit - count)
            
            # Calculate reset time
            if self._requests[key]:
                oldest = min(self._requests[key])
                reset = int((oldest + timedelta(seconds=window) - now).total_seconds())
            else:
                reset = window
                
            return count > limit, {
                "limit": limit,
                "remaining": remaining,
                "reset": reset
            }

    def _cleanup(self) -> None:
        """Remove entries older than the largest window."""
        now = datetime.utcnow()
        max_window = timedelta(hours=1)
        
        with self._lock:
            for key in list(self._requests.keys()):
                self._requests[key] = [
                    ts for ts in self._requests[key]
                    if now - ts < max_window
                ]
                if not self._requests[key]:
                    del self._requests[key]

# Global rate limiter instance
_limiter = RateLimiter()

def rate_limit(
    limit: Optional[int] = None,
    window: Optional[int] = None,
    key_func: Optional[Callable] = None
):
    """Rate limiting decorator for Flask routes."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_app.config.get('RATE_LIMIT_ENABLED', True):
                return f(*args, **kwargs)
            
            # Get rate limit settings
            rate_limit = limit or current_app.config.get('RATE_LIMIT_DEFAULT', 1000)
            time_window = window or current_app.config.get('RATE_LIMIT_WINDOW', 3600)
            
            # Get rate limit key
            if key_func:
                key = key_func()
            else:
                key = request.remote_addr
            
            # Check rate limit
            is_limited, info = _limiter.is_rate_limited(key, rate_limit, time_window)
            
            # Set rate limit headers
            response = current_app.make_response(f(*args, **kwargs) if not is_limited else 
                {"error": "Rate limit exceeded"})
            
            response.headers.update({
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": str(info["remaining"]),
                "X-RateLimit-Reset": str(info["reset"])
            })
            
            if is_limited:
                response.status_code = 429
                response.headers["Retry-After"] = str(info["reset"])
                logger.warning(f"Rate limit exceeded for {key}")
            
            return response
        return decorated_function
    return decorator