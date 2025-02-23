from functools import wraps
from typing import Callable, TypeVar, Any, List, cast
from flask import current_app, request, jsonify
from src.types.responses import ErrorResponse, ResponseType

F = TypeVar('F', bound=Callable[..., Any])

def db_transaction(f: F) -> F:
    """Decorator to handle database transactions."""
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        try:
            result = f(*args, **kwargs)
            return result
        except Exception as e:
            current_app.logger.error(f"Transaction error: {str(e)}")
            raise
    return decorated_function

F = TypeVar('F', bound=Callable[..., ResponseType])

def validate_form_data(required_fields: List[str]) -> Callable[[F], F]:
    def decorator(f: F) -> F:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> ResponseType:
            missing = [field for field in required_fields if not request.form.get(field)]
            if missing:
                error: ErrorResponse = {
                    "error": "Missing required fields",
                    "details": {"missing": missing}
                }
                return jsonify(error), 400
            return f(*args, **kwargs)
        return cast(F, decorated_function)
    return decorator
