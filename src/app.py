from flask import Flask, render_template
from neo4j import GraphDatabase
import os
from src.blueprints.auth import auth_bp
from src.blueprints.api import api_bp
from src.blueprints.items import bp as items_bp
from src.blueprints.optimizer import optimizer_bp
from src.core.limiter import InMemoryRateLimiter

app = Flask(__name__)

# Basic config
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
    NEO4J_URI=os.environ.get('NEO4J_URI', 'bolt://neo4j:7687'),
    NEO4J_USER=os.environ.get('NEO4J_USER', 'neo4j'),
    NEO4J_PASSWORD=os.environ.get('NEO4J_PASSWORD', 'password'),
    RATE_LIMIT_ENABLED=True,
    RATE_LIMIT_DEFAULT=1000,
    RATE_LIMIT_WINDOW=3600
)

# Database connection
def get_db():
    if not hasattr(app, 'neo4j_db'):
        app.neo4j_db = GraphDatabase.driver(
            app.config['NEO4J_URI'],
            auth=(app.config['NEO4J_USER'], app.config['NEO4J_PASSWORD'])
        )
    return app.neo4j_db

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(items_bp, url_prefix='/items')
app.register_blueprint(optimizer_bp, url_prefix='/optimize')

# Basic routes
@app.route('/')
def index():
    return render_template('index.html')

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

# Cleanup on shutdown
@app.teardown_appcontext
def close_db(error):
    if hasattr(app, 'neo4j_db'):
        app.neo4j_db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)