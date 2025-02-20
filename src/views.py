from flask import Blueprint

def register_blueprints(app):
    # Example blueprint registration
    from src.views.example import example_blueprint
    app.register_blueprint(example_blueprint)

# Define other blueprints here
