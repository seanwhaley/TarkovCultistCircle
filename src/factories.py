from neo4j import GraphDatabase
from flask import Flask
from src.db import Neo4jDB
from flask_cors import CORS
from src.application.extensions import extensions
from src.views.main.main_views import main_bp
from src.views.api.api_views import api_bp

class ApplicationFactory:
    """Single responsibility factory for application components"""
    
    @staticmethod
    def init_database(app):
        """Initialize database with app configuration"""
        db = extensions.get_db()
        db.initialize(
            app.config['NEO4J_URI'],
            app.config['NEO4J_USER'],
            app.config['NEO4J_PASSWORD']
        )
        app.db = db
        return db

    @staticmethod
    def init_cors(app):
        """Initialize CORS settings"""
        CORS(app)

    @staticmethod
    def register_blueprints(app):
        """Register all blueprints"""
        blueprints = [
            (main_bp, ''),
            (api_bp, '/api'),
        ]
        
        for blueprint, url_prefix in blueprints:
            app.register_blueprint(blueprint, url_prefix=url_prefix)

    @staticmethod
    def init_app(app):
        """Initialize all application components"""
        ApplicationFactory.init_database(app)
        ApplicationFactory.init_cors(app)
        ApplicationFactory.register_blueprints(app)
