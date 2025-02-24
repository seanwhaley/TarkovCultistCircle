"""Flask application factory."""
from flask import Flask
from flask_cors import CORS
from flask_sockets import Sockets
from src.blueprints.auth import auth_bp
from src.blueprints.api import api_bp
from src.blueprints.items import bp as items_bp
from src.blueprints.optimizer import optimizer_bp
from src.database import init_db
from src.core.errors import register_error_handlers
from src.core.scheduler import SchedulerManager
from src.core.tasks import TaskManager
import logging

def create_app(config_object=None):
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    if config_object:
        app.config.from_object(config_object)
    
    # Configure logging
    logging.basicConfig(
        level=app.config.get('LOG_LEVEL', 'INFO'),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize extensions
    CORS(app)
    sockets = Sockets(app)
    
    # Initialize core components
    init_db(app)
    register_error_handlers(app)
    
    # Initialize task manager
    task_manager = TaskManager(
        max_workers=app.config.get('MAX_WORKERS', 3)
    )
    app.config['task_manager'] = task_manager
    
    # Initialize and start scheduler
    scheduler = SchedulerManager(app.config)
    scheduler.start()
    app.config['scheduler'] = scheduler
    
    # Register cleanup on shutdown
    @app.teardown_appcontext
    def shutdown_scheduler(exception=None):
        scheduler = app.config.get('scheduler')
        if scheduler:
            scheduler.stop()
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(items_bp, url_prefix='/items')
    app.register_blueprint(optimizer_bp, url_prefix='/optimize')
    
    # Register WebSocket routes
    @sockets.route('/ws/market')
    def market_socket(ws):
        from src.core.websocket import manager
        client_id = str(uuid.uuid4())
        manager.connect(client_id, ws)
        try:
            while not ws.closed:
                message = ws.receive()
                if message:
                    data = json.loads(message)
                    if data.get('type') == 'subscribe':
                        manager.subscribe(client_id, data.get('item_id'))
                    elif data.get('type') == 'unsubscribe':
                        manager.unsubscribe(client_id, data.get('item_id'))
        finally:
            manager.disconnect(client_id)
    
    return app
