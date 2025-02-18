def register_blueprints(app):
    """Register all blueprints with the application"""
    from src.views.api.api_routes import api_bp
    from src.views.pages.page_routes import pages_bp
    from src.views.debug.debug_routes import debug_bp

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(pages_bp, url_prefix='/')
    app.register_blueprint(debug_bp, url_prefix='/debug')
