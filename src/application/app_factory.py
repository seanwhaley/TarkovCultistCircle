import os
import click
from flask import Flask
from flask.cli import with_appcontext
from flask_cors import CORS
from src.config import config  # Updated import
from src.core.database import Neo4jDB
from src.core.error_handlers import register_error_handlers
from src.core.graphql import GraphQLClient
from src.utils.logging import setup_logging

class ApplicationFactory:
    """Single responsibility factory for application components"""
    
    @staticmethod
    def create_app(config_name=None):
        """Create and configure the Flask application"""
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
        
        return app

    @staticmethod
    def run_app(app=None):
        """Run the Flask application"""
        if app is None:
            app = ApplicationFactory.create_app()
        
        host = os.getenv('FLASK_HOST', '0.0.0.0')
        port = int(os.getenv('FLASK_PORT', 5000))
        debug = app.config.get('DEBUG', False)
        
        app.run(host=host, port=port, debug=debug)

    @staticmethod
    def _init_logging(app):
        """Initialize application logging"""
        setup_logging(app)

    @staticmethod
    def _init_database(app):
        """Initialize database connection"""
        db = Neo4jDB()
        db.initialize(
            app.config['NEO4J_URI'],
            app.config['NEO4J_USER'],
            app.config['NEO4J_PASSWORD']
        )
        app.db = db
        return db

    @staticmethod
    def _init_cors(app):
        """Initialize CORS settings"""
        CORS(app)

    @staticmethod
    def _register_blueprints(app):
        """Register all blueprints"""
        from src.views import register_blueprints
        register_blueprints(app)

    @staticmethod
    def _register_error_handlers(app):
        """Register error handlers"""
        register_error_handlers(app)

    @staticmethod
    def _register_cli_commands(app):
        """Register Flask CLI commands"""
        @app.cli.command('ingest-data')
        @with_appcontext
        def ingest_data_command():
            """Fetch data from Tarkov API and store in Neo4j."""
            click.echo('Fetching data from Tarkov API...')
            
            client = GraphQLClient()
            result = client.execute_query()
            
            if not result or 'data' not in result or 'items' not in result['data']:
                click.echo('Invalid response format')
                return
                
            items = result['data']['items']
            click.echo(f'Found {len(items)} items')
            
            try:
                with app.db.get_session() as session:
                    # Clean existing data
                    session.run("MATCH (i:Item) DETACH DELETE i")
                    
                    # Create items
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
