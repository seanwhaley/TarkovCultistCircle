"""Centralized logging configuration."""
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any, Dict
from flask import Flask, request, has_request_context
import structlog
from pythonjsonlogger import jsonlogger

class RequestFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter that includes request context."""
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)
        
        if has_request_context():
            log_record['endpoint'] = request.endpoint
            log_record['method'] = request.method
            log_record['path'] = request.path
            log_record['ip'] = request.remote_addr

        log_record['logger'] = record.name
        log_record['level'] = record.levelname

def setup_logging(app: Flask) -> None:
    """Configure application logging with both structured and standard logging."""
    config = app.config
    log_dir = Path(config['LOG_DIR'])
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(indent=config.get('LOG_JSON_INDENT'))
    ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging handlers
    formatter = RequestFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s',
        json_indent=config.get('LOG_JSON_INDENT')
    )

    # Application log handler
    app_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'app.log',
        maxBytes=config['LOG_MAX_SIZE'],
        backupCount=config['LOG_BACKUP_COUNT']
    )
    app_handler.setFormatter(formatter)

    # Error log handler
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'error.log',
        maxBytes=config['LOG_MAX_SIZE'],
        backupCount=config['LOG_BACKUP_COUNT']
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers = [console_handler, app_handler, error_handler]
    root_logger.setLevel(config['LOG_LEVEL'])

    # Quiet some noisy loggers
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('neo4j').setLevel(logging.WARNING)

    # Register request logging
    @app.before_request
    def log_request():
        app.logger.info('Request started', 
            extra={
                'endpoint': request.endpoint,
                'method': request.method,
                'path': request.path
            }
        )

    @app.after_request
    def log_response(response):
        app.logger.info('Request finished',
            extra={
                'status': response.status_code,
                'size': response.content_length
            }
        )
        return response

def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
