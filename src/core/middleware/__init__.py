"""Core middleware components."""
from functools import wraps
from flask import request, current_app
from typing import Callable

def request_logger(f: Callable) -> Callable:
    """Log incoming requests."""
    @wraps(f)
    def decorated(*args, **kwargs):
        current_app.logger.info(f"{request.method} {request.path}")
        return f(*args, **kwargs)
    return decorated