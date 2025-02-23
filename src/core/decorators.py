"""Essential decorators for database operations and basic validation."""
from functools import wraps
from typing import Any, Callable, Dict, Type

def db_transaction(f: Callable) -> Callable:
    """Simple database transaction decorator."""
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        db = kwargs.get('db')
        if not db:
            raise ValueError("Database connection required")
            
        with db.transaction():
            return f(*args, **kwargs)
    return decorated_function

def validate_form_data(schema: Dict[str, Type]) -> Callable:
    """Basic type validation for form data."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(data: Dict, *args: Any, **kwargs: Any) -> Any:
            for field, field_type in schema.items():
                if field in data and not isinstance(data[field], field_type):
                    raise ValueError(f"Invalid type for {field}")
            return f(data, *args, **kwargs)
        return decorated_function
    return decorator
