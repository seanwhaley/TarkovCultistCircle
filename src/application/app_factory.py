# Standard library imports
import os
import logging
from typing import Optional

# Third-party imports
import click
from flask import Flask, render_template
from flask.cli import with_appcontext
from flask_cors import CORS
from flask_graphql import GraphQLView
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from neo4j import GraphDatabase

# Local imports
from src.config.config import config
from src.core.database import Neo4jDB
from src.core.error_handlers import register_error_handlers
from src.core.graphql import GraphQLClient
from src.graphql.schema import schema
from src.utils.logging import setup_logging
from src.views import register_blueprints

class ApplicationFactory:
    """Single responsibility factory for application components"""
    
    @staticmethod
    def create_app(config_name: Optional[str] = None) -> Flask:
        if config_name is None:
            config_name = os.getenv('FLASK_ENV', 'development')

        app = Flask(__name__,
                   template_folder='../src/templates',  # Ensure this points to the correct location
                   static_folder='../static')
        
        # Load configuration and initialize components
        app.config.from_object(config[config_name])  # Use the config dictionary
        
        # Enable debug mode for detailed error messages
        app.config['DEBUG'] = True
        
        # Initialize in specific order
        ApplicationFactory._init_logging(app)
        ApplicationFactory._init_database(app)
        ApplicationFactory._init_cors(app)
        ApplicationFactory._register_blueprints(app)
        ApplicationFactory._register_error_handlers(app)
        ApplicationFactory._register_cli_commands(app)
        
        # Initialize extensions
        jwt = JWTManager(app)
        db = SQLAlchemy(app)
        migrate = Migrate(app, db)

        # Initialize Neo4j driver with error handling
        try:
            neo4j_driver = GraphDatabase.driver(app.config['NEO4J_URI'], auth=(app.config['NEO4J_USER'], app.config['NEO4J_PASSWORD']))
        except Exception as e:
            logging.error(f"Failed to initialize Neo4j driver: {e}")
            raise

        # Add GraphQL endpoint
        app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

        # Define routes
        @app.route('/')
        def index():
            return render_template('index.html')

        return app

    @staticmethod
    def run_app(app: Optional[Flask] = None) -> None:
        if app is None:
            app = ApplicationFactory.create_app()
        
        host = os.getenv('FLASK_HOST', '0.0.0.0')
        port = int(os.getenv('FLASK_PORT', 5000))
        debug = app.config.get('DEBUG', False)
        
        app.run(host=host, port=port, debug=debug)

    @staticmethod
    def _init_logging(app: Flask) -> None:
        setup_logging(app)

    @staticmethod
    def _init_database(app: Flask) -> Neo4jDB:
        db = Neo4jDB()
        db.initialize(
            app.config['NEO4J_URI'],
            app.config['NEO4J_USER'],
            app.config['NEO4J_PASSWORD']
        )
        app.config['db'] = db
        return db

    @staticmethod
    def _init_cors(app: Flask) -> None:
        CORS(app)

    @staticmethod
    def _register_blueprints(app: Flask) -> None:
        from src.views import register_blueprints
        register_blueprints(app)

    @staticmethod
    def _register_error_handlers(app: Flask) -> None:
        register_error_handlers(app)

    @staticmethod
    def _register_cli_commands(app: Flask) -> None:
        @app.cli.command('ingest-data')
        @with_appcontext
        def ingest_data_command() -> None:
            click.echo('Fetching data from Tarkov API...')
            
            client = GraphQLClient()
            result = client.execute_query()
            
            if not result or 'data' not in result or 'items' not in result['data']:
                click.echo('Invalid response format')
                return
                
            items = result['data']['items']
            click.echo(f'Found {len(items)} items')
            
            try:
                with app.config['db'].get_session() as session:
                    session.run("MATCH (i:Item) DETACH DELETE i")
                    
                    for item in items:
                        query = """
                        CREATE (i:Item {
                            id: $id,
                            name: $name,
                            basePrice: toString($basePrice),
                            lastLowPrice: toString($lastLowPrice),
                            avg24hPrice: toString($avg24hPrice),
                            updated: $updated
                        })
                        """
                        session.run(query, parameters=item)
                        
                click.echo('Successfully ingested data into Neo4j')
            except Exception as e:
                click.echo(f'Error saving to Neo4j: {str(e)}')

create_app = ApplicationFactory.create_app
