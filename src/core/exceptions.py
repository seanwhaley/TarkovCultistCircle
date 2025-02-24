"""Core exceptions with enhanced relationship and market operation handling."""
from typing import Optional, Dict, Any, List

class BaseError(Exception):
    """Base exception class."""
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

class DatabaseError(BaseError):
    """Base class for database exceptions."""
    pass

class ConnectionError(DatabaseError):
    """Raised when database connection fails."""
    pass

class QueryError(DatabaseError):
    """Raised when a database query fails."""
    pass

class ValidationError(BaseError):
    """Raised when data validation fails."""
    def __init__(
        self,
        message: str,
        field_errors: Optional[Dict[str, List[str]]] = None
    ) -> None:
        super().__init__(message, "VALIDATION_ERROR", {"fields": field_errors})

class RelationshipError(DatabaseError):
    """Raised when relationship operations fail."""
    def __init__(
        self,
        message: str,
        from_node: Optional[str] = None,
        to_node: Optional[str] = None,
        relationship_type: Optional[str] = None
    ) -> None:
        details = {
            "from_node": from_node,
            "to_node": to_node,
            "relationship_type": relationship_type
        }
        super().__init__(message, "RELATIONSHIP_ERROR", details)

class NotFoundError(BaseError):
    """Raised when a resource is not found."""
    def __init__(self, message: str, resource_type: Optional[str] = None) -> None:
        super().__init__(message, "NOT_FOUND", {"resource_type": resource_type})

class OptimizationError(BaseError):
    """Raised when market optimization fails."""
    def __init__(
        self,
        message: str,
        optimization_type: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message,
            "OPTIMIZATION_ERROR",
            {
                "type": optimization_type,
                "parameters": parameters
            }
        )

class MarketError(BaseError):
    """Raised when market operations fail."""
    def __init__(
        self,
        message: str,
        item_id: Optional[str] = None,
        operation: Optional[str] = None,
        market_data: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message,
            "MARKET_ERROR",
            {
                "item_id": item_id,
                "operation": operation,
                "market_data": market_data
            }
        )

class PriceUpdateError(MarketError):
    """Raised when price updates fail."""
    def __init__(
        self,
        message: str,
        item_id: str,
        price_data: Dict[str, Any]
    ) -> None:
        super().__init__(
            message,
            item_id,
            "price_update",
            price_data
        )

class BlacklistError(MarketError):
    """Raised when blacklist operations fail."""
    pass

class ConfigurationError(BaseError):
    """Raised when configuration is invalid."""
    pass

class AuthenticationError(BaseError):
    """Raised when authentication fails."""
    pass

class AuthorizationError(BaseError):
    """Raised when authorization fails."""
    pass

class RateLimitError(BaseError):
    """Raised when rate limits are exceeded."""
    def __init__(
        self,
        message: str,
        limit: int,
        reset_time: Optional[int] = None
    ) -> None:
        super().__init__(
            message,
            "RATE_LIMIT_EXCEEDED",
            {
                "limit": limit,
                "reset_time": reset_time
            }
        )