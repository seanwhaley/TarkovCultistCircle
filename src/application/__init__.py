from flask import Flask
from src.config import config
from src.application.app_factory import ApplicationFactory
from src.core.error_handlers import register_error_handlers

def create_app(config_name='default'):
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Load config
    app.config.from_object(config[config_name])
    
    # Initialize application using factory
    ApplicationFactory.init_app(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

__all__ = ['ApplicationFactory']
