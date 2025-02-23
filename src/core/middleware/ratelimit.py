"""Rate limiting middleware using in-memory storage."""
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.limiter import rate_limiter
from src.core.exceptions import RateLimitError

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using in-memory storage."""

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope, receive=receive)
        
        try:
            # Check rate limit
            is_limited, rate_info = rate_limiter.is_rate_limited(request)
            
            if is_limited:
                raise RateLimitError(
                    message="Rate limit exceeded",
                    details=rate_info
                )

            # Process request
            response = await self.app(scope, receive, send)
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
            response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])
            
            return response

        except RateLimitError as e:
            raise e
        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            # On errors, allow the request but log the error
            return await self.app(scope, receive, send)