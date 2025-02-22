"""TarkovCultistCircle application package."""
import logging
from typing import Optional
from flask import Flask
from src.config import Config
from src.blueprints import register_blueprints
from src.core.extensions import init_extensions
from src.core.logging import setup_logging

__version__ = '0.1.0'
logger = logging.getLogger(__name__)

def create_app(config_object: Optional[object] = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object or Config)
    
    setup_logging(app)
    init_extensions(app)
    register_blueprints(app)
    
    return app
