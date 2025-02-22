from typing import Dict, List
import logging
from importlib import import_module
from flask import Blueprint, Flask
from src.core.api import api_blueprint

logger = logging.getLogger(__name__)

def register_blueprints(app: Flask) -> None:
    """
    Register all blueprints for application
    
    Args:
        app: Flask application instance
    """
    blueprints: Dict[str, str] = {
        'items': 'src.views.items.routes',
        'market': 'src.views.market.routes',
        'auth': 'src.views.auth.routes',
        'admin': 'src.views.admin.routes'
    }
    
    try:
        for name, module_path in blueprints.items():
            module = import_module(module_path)
            if name != 'admin':
                wrapped_bp: Blueprint = api_blueprint(name)
                wrapped_bp.register_blueprint(module.bp)  # type: ignore
                app.register_blueprint(wrapped_bp)
                logger.info(f"Registered API blueprint: {name}")
            else:
                app.register_blueprint(module.bp)  # type: ignore
                logger.info("Registered admin blueprint")
                
    except Exception as e:
        logger.error(f"Failed to register blueprints: {str(e)}")
        raise

# Export views
from src.views.items import (
    ItemListView, ItemDetailView, 
    ItemCreateView, ItemUpdateView
)
from src.views.market import (
    MarketOverviewView, PriceHistoryView
)

__all__ = [
    'register_blueprints',
    'ItemListView',
    'ItemDetailView',
    'ItemCreateView',
    'ItemUpdateView',
    'MarketOverviewView',
    'PriceHistoryView'
]
