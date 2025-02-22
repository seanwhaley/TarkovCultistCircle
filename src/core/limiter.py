"""Enhanced rate limiting with Starlette."""
from typing import Callable, Dict, Optional, Union
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict
from dataclasses import dataclass
import structlog
from starlette.requests import Request
from starlette.responses import Response

from src.core.logging import get_logger

logger = get_logger(__name__)

@dataclass
class RateLimit:
    """Rate limit configuration."""
    calls: int
    period: int  # in seconds
    key_func: Optional[Callable] = None

class RateLimiter:
    """Advanced rate limiter with multiple limit types."""
    
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self._cleanup_task = None

    async def start(self):
        """Start cleanup task."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop(self):
        """Stop cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    async def _cleanup_loop(self):
        """Periodically clean up old request records."""
        while True:
            try:
                now = datetime.utcnow()
                for key in list(self.requests.keys()):
                    self.requests[key] = [
                        ts for ts in self.requests[key]
                        if now - ts < timedelta(hours=1)
                    ]
                    if not self.requests[key]:
                        del self.requests[key]
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Rate limiter cleanup error")
                await asyncio.sleep(60)

    def _get_key(self, request: Request, key_func: Optional[Callable] = None) -> str:
        """Get rate limit key for request."""
        if key_func:
            return key_func(request)
        return f"{request.client.host}"

    async def is_rate_limited(
        self, 
        request: Request,
        limit: Union[RateLimit, Dict[str, RateLimit]]
    ) -> Optional[Response]:
        """Check if request is rate limited."""
        if isinstance(limit, dict):
            # Check multiple rate limits
            for limit_type, rate_limit in limit.items():
                key = f"{self._get_key(request, rate_limit.key_func)}:{limit_type}"
                if response := await self._check_limit(request, key, rate_limit):
                    return response
            return None
        else:
            # Single rate limit
            key = self._get_key(request, limit.key_func)
            return await self._check_limit(request, key, limit)

    async def _check_limit(
        self,
        request: Request,
        key: str,
        limit: RateLimit
    ) -> Optional[Response]:
        """Check single rate limit."""
        now = datetime.utcnow()
        requests = self.requests[key]
        
        # Remove old requests
        window_start = now - timedelta(seconds=limit.period)
        requests = [ts for ts in requests if ts > window_start]
        
        if len(requests) >= limit.calls:
            reset_time = min(requests) + timedelta(seconds=limit.period)
            reset_seconds = int((reset_time - now).total_seconds())
            
            logger.warning("Rate limit exceeded", 
                         key=key,
                         limit=limit.calls,
                         period=limit.period,
                         reset_in=reset_seconds)
            
            return Response(
                status_code=429,
                content={"error": "Too many requests"},
                headers={
                    "X-RateLimit-Limit": str(limit.calls),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_seconds)
                }
            )
        
        self.requests[key] = requests + [now]
        return None

rate_limiter = RateLimiter()
