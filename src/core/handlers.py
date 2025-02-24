"""Flask error handling configuration."""
from typing import Any, Dict, Optional
from flask import jsonify, current_app
import logging
from neo4j.exceptions import ServiceUnavailable

from src.core.exceptions import (
    AppException,
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
    NotFoundError,
    RateLimitError,
    ValidationError
)

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Register Flask error handlers."""
    
    @app.errorhandler(AppException)
    def handle_app_error(error):
        response = jsonify({
            "error": error.message,
            "details": error.details or {},
            "status_code": error.status_code
        })
        response.status_code = error.status_code
        return response

    @app.errorhandler(ServiceUnavailable)
    def handle_database_error(error):
        response = jsonify({
            "error": "Database service unavailable",
            "details": {"error": str(error)},
            "status_code": 503
        })
        response.status_code = 503
        return response

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        response = jsonify({
            "error": error.message,
            "details": error.details or {},
            "status_code": 422
        })
        response.status_code = 422
        return response

    @app.errorhandler(AuthenticationError)
    def handle_authentication_error(error):
        response = jsonify({
            "error": error.message,
            "details": error.details or {},
            "status_code": 401
        })
        response.status_code = 401
        response.headers["WWW-Authenticate"] = "Bearer"
        return response

    @app.errorhandler(AuthorizationError)
    def handle_authorization_error(error):
        response = jsonify({
            "error": error.message,
            "details": error.details or {},
            "status_code": 403
        })
        response.status_code = 403
        return response

    @app.errorhandler(NotFoundError)
    def handle_not_found_error(error):
        response = jsonify({
            "error": error.message,
            "details": error.details or {},
            "status_code": 404
        })
        response.status_code = 404
        return response

    @app.errorhandler(RateLimitError)
    def handle_rate_limit_error(error):
        response = jsonify({
            "error": error.message,
            "details": error.details or {},
            "status_code": 429
        })
        response.status_code = 429
        response.headers["Retry-After"] = str(error.details.get("retry_after", 3600))
        return response

    @app.errorhandler(404)
    def not_found(error):
        response = jsonify({
            "error": "Resource not found",
            "status_code": 404
        })
        response.status_code = 404
        return response

    @app.errorhandler(500)
    def internal_error(error):
        logger.exception("Internal server error")
        response = jsonify({
            "error": "Internal server error",
            "status_code": 500
        })
        response.status_code = 500
        return response