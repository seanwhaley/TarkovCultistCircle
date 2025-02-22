from functools import wraps
from flask import request, current_app
import time
from collections import defaultdict
import threading
import datetime

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.lock = threading.Lock()

    def is_rate_limited(self, key: str, limit: int, period: int) -> bool:
        now = datetime.datetime.now()
        cutoff = now - datetime.timedelta(seconds=period)
        
        with self.lock:
            # Clean old requests
            self.requests[key] = [req_time for req_time in self.requests[key] if req_time > cutoff]
            
            # Check if limit exceeded
            if len(self.requests[key]) >= limit:
                return True
            
            # Add new request
            self.requests[key].append(now)
            return False

rate_limiter = RateLimiter()

def rate_limit(limit, period):
    """Rate limiting decorator using in-memory storage"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_app.config.get('RATE_LIMIT_ENABLED', True):
                return f(*args, **kwargs)

            key = f"{request.remote_addr}:{f.__name__}"
            if rate_limiter.is_rate_limited(key, limit, period):
                return {'error': 'Rate limit exceeded'}, 429

            return f(*args, **kwargs)
        return decorated_function
    return decorator
