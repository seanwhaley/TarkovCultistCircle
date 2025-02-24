"""Application factory module."""
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_sockets import Sockets

from src.config import Config
from src.core.logging import setup_logging
from src.core.extensions import init_extensions
from src.database import init_db
from src.blueprints import register_blueprints
from src.core.scheduler import SchedulerManager
from src.core.tasks import TaskManager
from src.core.websocket import ConnectionManager

class ApplicationFactory:
    """Factory for creating and configuring Flask applications."""

    @staticmethod
    def create_app(config_object=None) -> Flask:
        """Create and configure a new Flask application instance."""
        app = Flask(__name__)
        
        # Load configuration
        app.config.from_object(config_object or Config)
        
        # Setup logging first for better debugging
        setup_logging(app)
        
        # Initialize extensions
        init_extensions(app)
        CORS(app)
        sockets = Sockets(app)
        
        # Initialize database
        init_db(app)
        
        # Initialize task manager
        task_manager = TaskManager(
            max_workers=app.config.get('MAX_WORKERS', 3)
        )
        app.config['task_manager'] = task_manager
        
        # Initialize and start scheduler
        scheduler = SchedulerManager(app.config)
        scheduler.start()
        app.config['scheduler'] = scheduler
        
        # Initialize WebSocket manager
        websocket_manager = ConnectionManager()
        app.config['websocket_manager'] = websocket_manager
        
        # Register blueprints
        register_blueprints(app)
        
        # Register WebSocket routes
        ApplicationFactory._register_websocket_routes(app, sockets)
        
        # Register cleanup
        ApplicationFactory._register_cleanup_handlers(app)
        
        return app

    @staticmethod
    def _register_websocket_routes(app: Flask, sockets: Sockets) -> None:
        """Register WebSocket routes."""
        @sockets.route('/ws/market')
        def market_socket(ws):
            websocket_manager = app.config['websocket_manager']
            websocket_manager.handle_connection(ws)

    @staticmethod
    def _register_cleanup_handlers(app: Flask) -> None:
        """Register cleanup handlers for application shutdown."""
        @app.teardown_appcontext
        def cleanup(exception=None):
            # Stop scheduler
            scheduler = app.config.get('scheduler')
            if scheduler:
                scheduler.stop()
            
            # Close database connections
            from src.database import Database
            Database.close()
