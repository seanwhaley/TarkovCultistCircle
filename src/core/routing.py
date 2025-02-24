"""Core routing functionality."""
from typing import Any, Callable, List
from flask import Blueprint
import structlog

logger = structlog.get_logger(__name__)

def register_blueprints(app, blueprints: List[Blueprint]) -> None:
    """
    Register Flask blueprints with the application.
    
    Args:
        app: Flask application instance
        blueprints: List of Blueprint instances to register
    """
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
        logger.info(f"Registered blueprint: {blueprint.name}")