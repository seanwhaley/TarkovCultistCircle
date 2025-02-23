import os
import logging
import logging.handlers
from datetime import datetime
from flask import Flask, request, has_request_context, current_app
from pythonjsonlogger import jsonlogger
from config.config import Config  # Updated import path

class RequestFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(RequestFormatter, self).add_fields(log_record, record, message_dict)
        
        if has_request_context():
            log_record['ip'] = request.remote_addr
            log_record['method'] = request.method
            log_record['url'] = request.url
            log_record['user_agent'] = request.headers.get('User-Agent')
            log_record['request_id'] = request.headers.get('X-Request-ID')
        
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name

def setup_logging(app: Flask):
    """Configure application logging"""
    config = app.config
    log_dir = os.path.dirname(config['LOG_FILE'])
    os.makedirs(log_dir, exist_ok=True)

    formatter = RequestFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s',
        json_indent=config.get('LOG_JSON_INDENT')
    )
    
    # Set up handlers with config values
    app_handler = logging.handlers.RotatingFileHandler(
        config['LOG_FILE'],
        maxBytes=config['LOG_MAX_SIZE'],
        backupCount=config['LOG_BACKUP_COUNT']
    )
    app_handler.setFormatter(formatter)
    
    # Application log
    app_log = logging.getLogger('tarkov_cultist')
    app_log.setLevel(logging.INFO)
    app_log.addHandler(app_handler)

    # Error log
    error_log = logging.getLogger('tarkov_cultist.error')
    error_log.setLevel(logging.ERROR)
    
    # File handler for error logs
    error_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'error.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    error_handler.setFormatter(formatter)
    error_log.addHandler(error_handler)

    # Access log middleware
    @app.before_request
    def log_request():
        app_log.info('Request started', extra={
            'endpoint': request.endpoint,
            'blueprint': request.blueprint,
            'content_length': request.content_length,
            'content_type': request.content_type
        })

    @app.after_request
    def log_response(response):
        app_log.info('Request finished', extra={
            'status': response.status_code,
            'content_length': response.content_length,
            'content_type': response.content_type
        })
        return response

    # Log unhandled exceptions
    @app.errorhandler(Exception)
    def log_exception(error):
        error_log.exception('Unhandled exception', extra={
            'error_type': error.__class__.__name__
        })
        raise error

    return app_log
