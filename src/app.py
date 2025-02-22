from flask import Flask, render_template
from neo4j import GraphDatabase
import os

app = Flask(__name__)

# Basic config
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
    NEO4J_URI=os.environ.get('NEO4J_URI', 'bolt://neo4j:7687'),
    NEO4J_USER=os.environ.get('NEO4J_USER', 'neo4j'),
    NEO4J_PASSWORD=os.environ.get('NEO4J_PASSWORD', 'password')
)

# Database connection
def get_db():
    if not hasattr(app, 'neo4j_db'):
        app.neo4j_db = GraphDatabase.driver(
            app.config['NEO4J_URI'],
            auth=(app.config['NEO4J_USER'], app.config['NEO4J_PASSWORD'])
        )
    return app.neo4j_db

# Basic routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/optimize')
def optimize():
    return render_template('optimizer/index.html')

@app.route('/items')
def items():
    with get_db().session() as session:
        result = session.run("MATCH (i:Item) RETURN i LIMIT 10")
        items = [record['i'] for record in result]
    return render_template('items/list.html', items=items)

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)