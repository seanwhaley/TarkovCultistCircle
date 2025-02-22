import logging
from flask import jsonify, render_template, request
from werkzeug.exceptions import HTTPException
from src.services.exceptions import (
    ItemServiceError,
    ValidationError,
    DatabaseError,
    ItemNotFoundError
)

logger = logging.getLogger('tarkov_cultist.error')

def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        logger.warning('Validation error', extra={'error': str(error)})
        if request.is_json or request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Validation error', 'message': str(error)}), 400
        return render_template('errors/400.html', error=error), 400

    @app.errorhandler(DatabaseError)
    def handle_database_error(error):
        logger.error('Database error', extra={'error': str(error)})
        if request.is_json or request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Database error', 'message': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(ItemNotFoundError)
    def handle_not_found_error(error):
        logger.info('Item not found', extra={'error': str(error)})
        if request.is_json or request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Not found', 'message': str(error)}), 404
        return render_template('errors/404.html', error=error), 404

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        logger.warning(f'HTTP error: {error.code}', extra={'error': str(error)})
        if request.is_json or request.headers.get('Accept') == 'application/json':
            return jsonify({'error': error.name, 'message': error.description}), error.code
        return render_template(f'errors/{error.code}.html', error=error), error.code

    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.exception('Unhandled exception')
        if request.is_json or request.headers.get('Accept') == 'application/json':
            return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500
        return render_template('errors/500.html'), 500
