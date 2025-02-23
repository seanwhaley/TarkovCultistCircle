"""Error handlers for database and application errors."""
import logging
from flask import jsonify, render_template, request
from werkzeug.exceptions import HTTPException
from src.database.exceptions import DatabaseError, ConnectionError, QueryError, ValidationError

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle database validation errors."""
        logger.warning(f'Validation error: {str(error)}')
        if request.is_json:
            return jsonify({'error': 'Validation error', 'details': error.details}), 400
        return render_template('errors/400.html', error=str(error)), 400
    
    @app.errorhandler(ConnectionError)
    def handle_connection_error(error):
        """Handle database connection errors."""
        logger.error(f'Database connection error: {str(error)}')
        if request.is_json:
            return jsonify({'error': 'Service unavailable', 'message': str(error)}), 503
        return render_template('errors/503.html'), 503
    
    @app.errorhandler(QueryError)
    def handle_query_error(error):
        """Handle database query errors."""
        logger.error(f'Database query error: {str(error)}')
        if request.is_json:
            return jsonify({'error': 'Database error', 'message': str(error)}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(DatabaseError)
    def handle_database_error(error):
        """Handle generic database errors."""
        logger.error(f'Database error: {str(error)}')
        if request.is_json:
            return jsonify({'error': 'Database error', 'message': 'An unexpected database error occurred'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors."""
        if request.is_json:
            return jsonify({'error': 'Not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle any unhandled exceptions."""
        logger.exception('Unhandled exception')
        if request.is_json:
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
