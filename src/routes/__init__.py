from flask import Flask
from .optimizer_routes import optimizer_bp
from .home_routes import home_bp
from ..views.debug.debug_routes import debug_bp
from ..views.api.api_routes import api_bp

def register_routes(app: Flask):
    app.register_blueprint(optimizer_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(debug_bp)
    app.register_blueprint(api_bp)
