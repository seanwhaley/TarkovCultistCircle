"""Blueprint registration module."""
from typing import List, Optional, Tuple, TypeVar
from flask import Flask, Blueprint

from src.blueprints.main import main_bp
from src.blueprints.auth import auth_bp
from src.blueprints.items import bp as items_bp
from src.blueprints.debug import debug_bp
from src.blueprints.optimizer import optimizer_bp
from src.blueprints.api import api_bp
from src.blueprints.errors import errors_bp
from src.blueprints.market import bp as market_bp

__all__ = ['register_blueprints', 'items_bp', 'auth_bp']

BlueprintType = TypeVar('BlueprintType', bound=Blueprint)

def register_blueprints(app: Flask) -> None:
    """Register all blueprints with the application."""
    blueprints: List[Tuple[Blueprint, Optional[str]]] = [
        (errors_bp, None),  # Error handlers must be registered first
        (main_bp, '/'),
        (auth_bp, '/auth'),
        (items_bp, '/items'),
        (optimizer_bp, '/optimizer'),
        (market_bp, '/market'),
        (api_bp, f"{app.config.get('API_PREFIX', '/api')}/{app.config.get('API_VERSION', 'v1')}")
    ]
    
    if app.config.get('DEBUG', False) and app.config.get('ENABLE_DEBUG_ROUTES', False):
        blueprints.append((debug_bp, '/debug'))

    for blueprint, url_prefix in blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix)
