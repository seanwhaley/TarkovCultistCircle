from datetime import datetime
import logging
from typing import Dict, Optional, Tuple, Union

from redis.asyncio import Redis
from fastapi import HTTPException, Request, status

from src.core.redis import RedisManager

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiting implementation using Redis."""
    
    def __init__(
        self,
        redis: Redis,
        key_prefix: str = "ratelimit:",
        default_limit: int = 1000,
        default_window: int = 3600
    ):
        self.redis = redis
        self.key_prefix = key_prefix
        self.default_limit = default_limit
        self.default_window = default_window

    async def _get_route_limits(self, path: str) -> Tuple[int, int]:
        """Get rate limits for a specific route."""
        # Define route-specific limits
        route_limits: Dict[str, Tuple[int, int]] = {
            # Auth endpoints
            "/auth/register": (3, 3600),  # 3 requests per hour
            "/auth/login": (10, 60),  # 10 requests per minute
            
            # Item endpoints
            "/items/": (1000, 3600),  # 1000 requests per hour
            "/items/price-override": (10, 60),  # 10 overrides per minute
            "/items/blacklist": (5, 60),  # 5 requests per minute
            "/items/lock": (5, 60),  # 5 requests per minute
            
            # Market endpoints
            "/market/analytics": (100, 60),  # 100 requests per minute
            "/market/price-history": (200, 60),  # 200 requests per minute
            
            # Optimizer endpoints
            "/optimize/calculate": (20, 60),  # 20 calculations per minute
            "/optimize/suggestions": (50, 60),  # 50 requests per minute
        }
        
        # Find matching route pattern
        for route, limits in route_limits.items():
            if path.startswith(route):
                return limits
        
        return (self.default_limit, self.default_window)

    def _get_client_identifier(self, request: Request) -> str:
        """Get unique identifier for the client."""
        # Try to get user ID if authenticated
        if hasattr(request.state, "user"):
            return f"user:{request.state.user.uid}"
            
        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0]}"
        return f"ip:{request.client.host}"

    async def is_rate_limited(
        self,
        request: Request,
        limit: Optional[int] = None,
        window: Optional[int] = None
    ) -> Tuple[bool, Dict[str, Union[int, str]]]:
        """
        Check if request should be rate limited.
        
        Returns:
            Tuple of (is_limited, rate_info)
        """
        # Skip rate limiting for excluded paths
        if request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):
            return False, {}
            
        # Get limits for the route
        route_limit, route_window = await self._get_route_limits(request.url.path)
        limit = limit or route_limit
        window = window or route_window
        
        # Build Redis key
        client_id = self._get_client_identifier(request)
        key = f"{self.key_prefix}{client_id}:{request.url.path}"
        
        try:
            # Get current count
            pipe = self.redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, window)
            current = await pipe.execute()
            count = int(current[0])
            
            # Check if limit exceeded
            is_limited = count > limit
            
            # Get TTL for reset time
            ttl = await self.redis.ttl(key)
            
            rate_info = {
                "limit": limit,
                "remaining": max(0, limit - count),
                "reset": ttl,
                "window": window
            }
            
            return is_limited, rate_info
            
        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            # On Redis errors, allow the request but log the error
            return False, {}

def rate_limit(
    limit: Optional[int] = None,
    window: Optional[int] = None
):
    """
    Rate limiting decorator for FastAPI endpoints.
    
    Args:
        limit: Maximum number of requests
        window: Time window in seconds
    """
    async def dependency(request: Request):
        redis = await RedisManager.get_redis()
        limiter = RateLimiter(redis)
        
        is_limited, rate_info = await limiter.is_rate_limited(
            request,
            limit=limit,
            window=window
        )
        
        if is_limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": str(rate_info["remaining"]),
                    "X-RateLimit-Reset": str(rate_info["reset"]),
                    "Retry-After": str(rate_info["reset"])
                }
            )
            
        # Add rate limit headers to successful responses
        request.state.rate_limit_info = rate_info
    
    return dependency