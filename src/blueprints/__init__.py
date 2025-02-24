"""Blueprint registration module."""
from typing import List
from flask import Flask, Blueprint

from .main import main_bp
from .auth import auth_bp
from .items import bp as items_bp
from .debug import debug_bp
from .optimizer import optimizer_bp
from .api import api_bp
from .errors import errors_bp
from .market import bp as market_bp

__all__ = ['register_blueprints']

def register_blueprints(app: Flask) -> None:
    """Register all blueprints with the application."""
    blueprints = [
        (errors_bp, None),  # Error handlers must be registered first
        (main_bp, '/'),
        (auth_bp, '/auth'),
        (items_bp, '/items'),
        (optimizer_bp, '/optimize'),
        (market_bp, '/market'),
        (api_bp, f"{app.config['API_PREFIX']}/{app.config['API_VERSION']}")
    ]

    # Register debug routes only in development
    if app.debug and app.config.get('ENABLE_DEBUG_ROUTES', False):
        blueprints.append((debug_bp, '/debug'))

    for blueprint, url_prefix in blueprints:
        app.register_blueprint(blueprint, url_prefix=url_prefix)
        app.logger.info(f"Registered blueprint: {blueprint.name} with prefix: {url_prefix}")
