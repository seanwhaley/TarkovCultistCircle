from datetime import datetime, timedelta
import logging
from typing import Callable, Optional

from fastapi import Request, Response
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.config import Settings
from src.core.exceptions import RateLimitError

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis."""

    def __init__(
        self,
        app,
        redis: Redis,
        settings: Settings,
        rate_limit_key_prefix: str = "ratelimit:",
        default_limit: int = 1000,
        default_period: int = 3600
    ):
        super().__init__(app)
        self.redis = redis
        self.settings = settings
        self.key_prefix = rate_limit_key_prefix
        self.default_limit = default_limit
        self.default_period = default_period

    async def get_route_limits(self, route: str) -> tuple[int, int]:
        """Get rate limits for a specific route."""
        # Example route-specific limits
        limits = {
            "/api/v1/items": (2000, 3600),  # 2000 requests per hour
            "/api/v1/auth/register": (3, 3600),  # 3 registrations per hour
            "/api/v1/optimize/calculate": (100, 3600),  # 100 calculations per hour
        }
        return limits.get(route, (self.default_limit, self.default_period))

    def get_client_id(self, request: Request) -> str:
        """Get client identifier from request."""
        # Try to get user ID from auth token first
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0]}"
        return f"ip:{request.client.host}"

    async def call_next(self, request: Request) -> Response:
        """Process the request through rate limiting."""
        # Skip rate limiting for certain paths
        if request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):
            return await self.app(request)

        client_id = self.get_client_id(request)
        limit, period = await self.get_route_limits(request.url.path)
        
        # Create Redis key
        key = f"{self.key_prefix}{client_id}:{request.url.path}"
        
        try:
            # Get current count
            count = await self.redis.get(key)
            count = int(count) if count else 0
            
            if count >= limit:
                raise RateLimitError(
                    message="Rate limit exceeded",
                    details={
                        "limit": limit,
                        "period": period,
                        "remaining": 0,
                        "reset": await self.redis.ttl(key)
                    }
                )
            
            # Increment counter
            pipe = self.redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, period)
            await pipe.execute()
            
            # Process request
            response = await self.app(request)
            
            # Add rate limit headers
            remaining = limit - (count + 1)
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(await self.redis.ttl(key))
            
            return response
            
        except RateLimitError as e:
            raise e
        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            # On Redis errors, allow the request but log the error
            return await self.app(request)