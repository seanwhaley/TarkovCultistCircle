"""Simple in-memory rate limiting."""
from datetime import datetime, timedelta
import threading
from typing import Dict, Tuple
from collections import defaultdict
from fastapi import Request

class RateLimiter:
    """Thread-safe in-memory rate limiter with simplified implementation."""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.lock = threading.Lock()
        
    def is_rate_limited(self, request: Request) -> Tuple[bool, Dict]:
        """Simple rate check - 1000 requests per hour per IP."""
        if request.url.path.startswith(("/docs", "/openapi.json")):
            return False, {}
            
        client_ip = request.client.host
        with self.lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(hours=1)
            
            # Clean old requests
            self.requests[client_ip] = [ts for ts in self.requests[client_ip] if ts > cutoff]
            current_count = len(self.requests[client_ip])
            
            # Check if limit exceeded
            if current_count >= 1000:
                reset_time = (min(self.requests[client_ip]) + timedelta(hours=1) - now).total_seconds()
                return True, {
                    "limit": 1000,
                    "remaining": 0,
                    "reset": int(reset_time)
                }
            
            # Add new request
            self.requests[client_ip].append(now)
            return False, {
                "limit": 1000,
                "remaining": 1000 - (current_count + 1),
                "reset": 3600
            }

# Global instance
rate_limiter = RateLimiter()
