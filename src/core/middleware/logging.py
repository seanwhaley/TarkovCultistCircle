import logging
import time
from typing import Callable, Optional
import uuid

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request logging."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Bind request context
        logger.bind(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_host=request.client.host,
            client_port=request.client.port
        )

        # Log request start
        logger.info(
            "request_started",
            query_params=dict(request.query_params),
            headers=dict(request.headers)
        )

        try:
            response = await call_next(request)
            
            # Calculate request duration
            duration = time.time() - start_time
            
            # Log request completion
            logger.info(
                "request_completed",
                status_code=response.status_code,
                duration=duration,
                response_headers=dict(response.headers)
            )
            
            # Add request ID and duration headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Request-Duration"] = f"{duration:.3f}"
            
            return response
            
        except Exception as e:
            # Log unhandled exceptions
            duration = time.time() - start_time
            logger.error(
                "request_failed",
                error=str(e),
                error_type=type(e).__name__,
                duration=duration,
                exc_info=True
            )
            raise