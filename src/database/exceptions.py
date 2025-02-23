"""Database exceptions with simplified error handling."""
from typing import Optional, Dict, Any

class DatabaseError(Exception):
    """Base class for database exceptions."""
    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - {self.details}"
        return self.message

class ConnectionError(DatabaseError):
    """Raised when database connection fails."""
    pass

class QueryError(DatabaseError):
    """Raised when a database query fails."""
    pass

class ValidationError(DatabaseError):
    """Raised when data validation fails."""
    pass
