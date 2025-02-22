from typing import Any, Callable, Dict, List, Optional, Type, Union
from fastapi import APIRouter, Depends, FastAPI, Request, Response
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse
import structlog

from src.core.exceptions import AppException
from src.core.responses import ErrorResponse
from src.core.validation import sanitize_query_params

logger = structlog.get_logger(__name__)

class ValidatedAPIRoute(APIRoute):
    """Custom API route with request validation and logging."""

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                # Sanitize query parameters
                request._query_params = sanitize_query_params(dict(request.query_params))
                
                # Execute route handler
                response: Response = await original_route_handler(request)
                
                # Log successful request
                logger.info(
                    "request_success",
                    path=request.url.path,
                    method=request.method,
                    status_code=response.status_code
                )
                
                return response
                
            except AppException as e:
                # Handle application exceptions
                error_response = ErrorResponse(
                    error=str(e),
                    details=e.details,
                    status_code=e.status_code
                )
                return JSONResponse(
                    status_code=e.status_code,
                    content=error_response.dict()
                )
                
            except Exception as e:
                # Log and handle unexpected errors
                logger.error(
                    "request_error",
                    path=request.url.path,
                    method=request.method,
                    error=str(e),
                    exc_info=True
                )
                error_response = ErrorResponse(
                    error="Internal server error",
                    status_code=500
                )
                return JSONResponse(
                    status_code=500,
                    content=error_response.dict()
                )

        return custom_route_handler

class APIRouterWithTags(APIRouter):
    """API Router with default tags and route class."""
    
    def __init__(
        self,
        *args: Any,
        prefix: str = "",
        tags: Optional[List[str]] = None,
        route_class: Type[APIRoute] = ValidatedAPIRoute,
        **kwargs: Any
    ) -> None:
        super().__init__(
            *args,
            prefix=prefix,
            tags=tags or [prefix.strip("/")],
            route_class=route_class,
            **kwargs
        )

def create_router(
    prefix: str,
    tags: Optional[List[str]] = None,
    dependencies: Optional[List[Depends]] = None,
    responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None
) -> APIRouterWithTags:
    """Create a new router with common configuration."""
    return APIRouterWithTags(
        prefix=prefix,
        tags=tags,
        dependencies=dependencies or [],
        responses=responses or {
            422: {"model": ErrorResponse},
            500: {"model": ErrorResponse}
        }
    )

def include_routers(app: FastAPI, routers: List[APIRouter]) -> None:
    """Include multiple routers in the application."""
    for router in routers:
        app.include_router(router)

def register_exception_handlers(
    app: FastAPI,
    handlers: Dict[Type[Exception], Callable]
) -> None:
    """Register multiple exception handlers."""
    for exc_class, handler in handlers.items():
        app.add_exception_handler(exc_class, handler)