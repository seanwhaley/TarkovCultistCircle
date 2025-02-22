"""Service layer exceptions."""

class ServiceError(Exception):
    """Base exception for service layer errors."""
    pass

class ValidationError(ServiceError):
    """Validation error in service layer."""
    pass

class ItemNotFoundError(ServiceError):
    """Item not found in database."""
    pass

class DatabaseError(ServiceError):
    """Database operation error."""
    pass

class ItemServiceError(ServiceError):
    """Item service specific error."""
    pass

class AuthenticationError(ServiceError):
    """Authentication related error."""
    pass

class OptimizationError(ServiceError):
    """Optimization calculation error."""
    pass

class AuthError(ServiceError):
    """Authorization related error."""
    pass

class ConfigurationError(ServiceError):
    """Configuration related error."""
    pass
