# This file is required to make this directory a Python package.

from .example import example_blueprint

def register_blueprints(app):
    # Example blueprint registration
    app.register_blueprint(example_blueprint)

# Ensure the package is correctly initialized
__all__ = ['register_blueprints']
