from typing import Optional, Any, TypeVar, Type, Dict
from types import TracebackType

E = TypeVar('E', bound='DatabaseError')

class DatabaseError(Exception):
    """Base class for database exceptions."""
    def __init__(
        self, 
        message: str, 
        original_error: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        self.message = message
        self.original_error = original_error
        self.context = context or {}
        super().__init__(message)

    def __str__(self) -> str:
        return f"{self.message} - {self.context}"

    @property
    def cause(self) -> Optional[Exception]:
        return self.original_error

    def with_traceback(self, tb: Optional[TracebackType]) -> 'DatabaseError':
        if self.original_error and tb:
            self.original_error.__traceback__ = tb
        return super().with_traceback(tb)

    @classmethod
    def from_exception(
        cls: Type[E], 
        exc: Exception, 
        message: Optional[str] = None
    ) -> E:
        return cls(
            message or str(exc),
            original_error=exc
        )

class AuthenticationError(DatabaseError):
    """Raised when database authentication fails."""
    pass

class ConnectionError(DatabaseError):
    """Raised when database connection fails."""
    pass

class QueryError(DatabaseError):
    """Raised when a database query fails."""
    pass

class TransactionError(DatabaseError):
    """Raised when a database transaction fails."""
    pass

class ValidationError(DatabaseError):
    """Raised when validation fails."""
    pass

class ConfigurationError(DatabaseError):
    """Raised when configuration is invalid."""
    pass

class SessionError(DatabaseError):
    """Raised when session operations fail."""
    pass
