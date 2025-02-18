import logging
import logging.handlers
from flask import has_request_context, request
from src.config import Config  # Updated import path

class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None
        return super().format(record)

def setup_logging(app):
    formatter = RequestFormatter(Config.LOG_FORMAT)
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        Config.LOG_FILE,
        maxBytes=1024 * 1024,
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(Config.LOG_LEVEL)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Set up app logger
    app.logger.setLevel(Config.LOG_LEVEL)
    for handler in root_logger.handlers:
        app.logger.addHandler(handler)
