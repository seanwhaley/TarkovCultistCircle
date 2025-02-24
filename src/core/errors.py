"""Core error handling for Flask application."""
from typing import Dict, Any, Optional
from flask import jsonify, current_app
import logging

logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base application error."""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

class ValidationError(AppError):
    """Validation error."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)

class AuthenticationError(AppError):
    """Authentication error."""
    def __init__(self, message: str = "Not authenticated"):
        super().__init__(message, status_code=401)

class AuthorizationError(AppError):
    """Authorization error."""
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, status_code=403)

class NotFoundError(AppError):
    """Resource not found error."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)

class RateLimitError(AppError):
    """Rate limit exceeded error."""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 3600):
        super().__init__(message, status_code=429, details={"retry_after": retry_after})

def register_error_handlers(app):
    """Register error handlers for the Flask application."""
    
    @app.errorhandler(AppError)
    def handle_app_error(error):
        response = {
            "error": error.message,
            "details": error.details,
            "status_code": error.status_code
        }
        return jsonify(response), error.status_code

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            "error": "Resource not found",
            "status_code": 404
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.exception("Internal server error")
        return jsonify({
            "error": "Internal server error",
            "status_code": 500
        }), 500

    @app.errorhandler(ValidationError)
    def validation_error(error):
        return jsonify({
            "error": error.message,
            "details": error.details,
            "status_code": 422
        }), 422

    @app.errorhandler(RateLimitError)
    def rate_limit_error(error):
        response = jsonify({
            "error": error.message,
            "details": error.details,
            "status_code": 429
        })
        response.headers["Retry-After"] = str(error.details.get("retry_after", 3600))
        return response, 429