from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from neo4j.exceptions import ServiceUnavailable

from src.core.exceptions import (
    AppException,
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
    NotFoundError,
    RateLimitError,
    ValidationError
)

def setup_exception_handlers(app: FastAPI) -> None:
    """Configure exception handlers for the FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """Handle application-specific exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.message,
                "details": exc.details or {},
                "status_code": exc.status_code
            }
        )

    @app.exception_handler(ServiceUnavailable)
    async def neo4j_unavailable_handler(request: Request, exc: ServiceUnavailable) -> JSONResponse:
        """Handle Neo4j service unavailable errors."""
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "message": "Database service unavailable",
                "details": {"error": str(exc)},
                "status_code": status.HTTP_503_SERVICE_UNAVAILABLE
            }
        )

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """Handle validation errors."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": exc.message,
                "details": exc.details or {},
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY
            }
        )

    @app.exception_handler(AuthenticationError)
    async def auth_exception_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
        """Handle authentication errors."""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "message": exc.message,
                "details": exc.details or {},
                "status_code": status.HTTP_401_UNAUTHORIZED
            },
            headers={"WWW-Authenticate": "Bearer"}
        )

    @app.exception_handler(AuthorizationError)
    async def authorization_exception_handler(request: Request, exc: AuthorizationError) -> JSONResponse:
        """Handle authorization errors."""
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "message": exc.message,
                "details": exc.details or {},
                "status_code": status.HTTP_403_FORBIDDEN
            }
        )

    @app.exception_handler(NotFoundError)
    async def not_found_exception_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        """Handle not found errors."""
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": exc.message,
                "details": exc.details or {},
                "status_code": status.HTTP_404_NOT_FOUND
            }
        )

    @app.exception_handler(RateLimitError)
    async def rate_limit_exception_handler(request: Request, exc: RateLimitError) -> JSONResponse:
        """Handle rate limit errors."""
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "message": exc.message,
                "details": exc.details or {},
                "status_code": status.HTTP_429_TOO_MANY_REQUESTS
            }
        )