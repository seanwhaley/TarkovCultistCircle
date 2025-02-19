from flask import Flask
from src.core.database import Neo4jDB
from src.core.responses import success_response, error_response

db = Neo4jDB()

def init_app(app: Flask):
    """Initialize application with all extensions and blueprints"""
    # Initialize extensions
    db.init_app(app)

    # Register blueprints with consistent prefixes
    from src.views.api import api_bp
    from src.views.pages import pages_bp
    from src.views.debug import debug_bp
    from src.views.optimizer import optimizer_bp
    from src.views.items import items_bp

    # Blueprints have url_prefix defined in their own files
    app.register_blueprint(api_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(debug_bp)
    app.register_blueprint(optimizer_bp)
    app.register_blueprint(items_bp)

    # Register error handlers
    from .error_handlers import register_error_handlers
    register_error_handlers(app)

    return app
