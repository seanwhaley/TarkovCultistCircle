import logging
import sys
from typing import Any, Dict, List, Callable, Union, Mapping, MutableMapping

import structlog
from pythonjsonlogger import jsonlogger

def setup_logging() -> None:
    """Configure structured logging for the application."""
    
    # Configure structlog processors with proper type hints
    processors: List[Callable] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]

    # Configure structlog with explicit typing
    structlog.configure(
        processors=processors,  # type: ignore
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging to JSON
    json_handler = logging.StreamHandler(sys.stdout)
    json_handler.setFormatter(
        jsonlogger.JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s',
            timestamp=True
        )
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers = [json_handler]
    root_logger.setLevel(logging.INFO)

    # Quiet some noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("neo4j").setLevel(logging.WARNING)