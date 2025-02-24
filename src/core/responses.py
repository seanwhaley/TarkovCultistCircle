"""Flask response utilities."""
from typing import Any, Dict, List, Optional, TypeVar, Generic
from dataclasses import dataclass
from flask import jsonify, make_response, Response

T = TypeVar('T')

@dataclass
class PaginatedResponse(Generic[T]):
    """Pagination response container."""
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response."""
        return {
            "items": self.items,
            "total": self.total,
            "page": self.page,
            "per_page": self.per_page,
            "pages": self.pages,
            "has_next": self.has_next,
            "has_prev": self.has_prev
        }

def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None
) -> Response:
    """Create a success response."""
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    return make_response(jsonify(response), status_code, headers or {})

def error_response(
    message: str,
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Response:
    """Create an error response."""
    response = {
        "success": False,
        "error": message,
        "details": details or {}
    }
    return make_response(jsonify(response), status_code, headers or {})

def paginated_response(
    data: PaginatedResponse[T],
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None
) -> Response:
    """Create a paginated response."""
    response = {
        "success": True,
        "data": data.to_dict()
    }
    return make_response(jsonify(response), status_code, headers or {})
