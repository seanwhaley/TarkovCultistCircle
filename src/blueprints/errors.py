# Standard library imports
import logging
from typing import Tuple, Dict, Any, Union

# Third-party imports
from flask import Blueprint, current_app, jsonify, render_template, request
from werkzeug.exceptions import HTTPException
from werkzeug.wrappers.response import Response

# Local imports
from src.core.exceptions import BaseAppException
from src.types.responses import ResponseType

errors_bp = Blueprint('errors', __name__)

@errors_bp.app_errorhandler(404)
def not_found_error(error: Any) -> ResponseType:
    if request.accept_mimetypes.accept_json and \
       not request.accept_mimetypes.accept_html:
        return jsonify({'error': 'Not found'}), 404
    return render_template('pages/errors/404.html'), 404

@errors_bp.app_errorhandler(403)
def forbidden_error(error: Any) -> ResponseType:
    if request.accept_mimetypes.accept_json and \
       not request.accept_mimetypes.accept_html:
        return jsonify({'error': 'Forbidden'}), 403
    return render_template('pages/errors/403.html'), 403

@errors_bp.app_errorhandler(500)
def internal_error(error: Any) -> ResponseType:
    logging.error(f"Internal server error: {str(error)}")
    if request.accept_mimetypes.accept_json and \
       not request.accept_mimetypes.accept_html:
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('pages/errors/500.html'), 500

@errors_bp.app_errorhandler(429)
def ratelimit_error(error: Any) -> ResponseType:
    if request.accept_mimetypes.accept_json and \
       not request.accept_mimetypes.accept_html:
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': str(error.description)
        }), 429
    return render_template('pages/errors/429.html', error=error.description), 429

# Custom error handler for API validation errors
@errors_bp.app_errorhandler(422)
def validation_error(error: Any) -> ResponseType:
    if request.accept_mimetypes.accept_json and \
       not request.accept_mimetypes.accept_html:
        return jsonify({
            'error': 'Validation error',
            'errors': error.description,
        }), 422
    return render_template('pages/errors/422.html', errors=error.description), 422
