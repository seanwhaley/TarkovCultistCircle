import re
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal, InvalidOperation
from datetime import datetime
import uuid

from pydantic import ValidationError
from src.core.exceptions import ValidationError as AppValidationError

def validate_uuid(value: str) -> bool:
    """Validate UUID string format."""
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False

def validate_price(price: Union[float, str, Decimal]) -> float:
    """Validate and normalize price value."""
    try:
        if isinstance(price, str):
            price = Decimal(price)
        price_float = float(price)
        if price_float <= 0:
            raise AppValidationError("Price must be greater than 0")
        return round(price_float, 2)
    except (InvalidOperation, ValueError):
        raise AppValidationError("Invalid price format")

def sanitize_string(value: str) -> str:
    """Sanitize string input."""
    # Remove potentially dangerous characters
    value = re.sub(r'[<>{}[\]\\]', '', value)
    # Limit length
    return value[:500]

def validate_date_range(
    start_date: Optional[str],
    end_date: Optional[str]
) -> tuple[datetime, datetime]:
    """Validate and parse date range."""
    try:
        if start_date:
            start = datetime.fromisoformat(start_date)
        else:
            start = datetime.now()

        if end_date:
            end = datetime.fromisoformat(end_date)
        else:
            end = datetime.now()

        if end < start:
            raise AppValidationError("End date must be after start date")

        return start, end
    except ValueError:
        raise AppValidationError("Invalid date format")

def validate_pagination_params(
    page: int,
    size: int,
    max_size: int = 100
) -> tuple[int, int]:
    """Validate pagination parameters."""
    if page < 1:
        raise AppValidationError("Page number must be greater than 0")
    if size < 1 or size > max_size:
        raise AppValidationError(f"Page size must be between 1 and {max_size}")
    return page, size

def validate_sort_params(
    sort_field: str,
    allowed_fields: List[str],
    default_field: str = "created_at"
) -> str:
    """Validate sort field parameter."""
    if not sort_field:
        return default_field
    if sort_field not in allowed_fields:
        raise AppValidationError(f"Invalid sort field. Allowed fields: {', '.join(allowed_fields)}")
    return sort_field

def sanitize_query_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize query parameters."""
    sanitized = {}
    for key, value in params.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_string(value)
        elif isinstance(value, (int, float, bool)):
            sanitized[key] = value
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_string(v) if isinstance(v, str) else v
                for v in value
            ]
    return sanitized

def validate_coordinates(lat: float, lon: float) -> bool:
    """Validate geographic coordinates."""
    if not -90 <= lat <= 90:
        raise AppValidationError("Latitude must be between -90 and 90")
    if not -180 <= lon <= 180:
        raise AppValidationError("Longitude must be between -180 and 180")
    return True

def validate_language_code(code: str) -> bool:
    """Validate ISO language code."""
    if not re.match(r'^[a-z]{2}(-[A-Z]{2})?$', code):
        raise AppValidationError("Invalid language code format")
    return True

def validate_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise AppValidationError("Invalid email format")
    return True

def validate_password_strength(password: str) -> bool:
    """Validate password strength."""
    if len(password) < 8:
        raise AppValidationError("Password must be at least 8 characters long")
    if not re.search(r'[A-Z]', password):
        raise AppValidationError("Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        raise AppValidationError("Password must contain at least one lowercase letter")
    if not re.search(r'\d', password):
        raise AppValidationError("Password must contain at least one number")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise AppValidationError("Password must contain at least one special character")
    return True