from flask import Blueprint, render_template, jsonify
from src.core.graphql import GraphQLClient
from src.config import Config
from src.core.database import Neo4jDB
from src.utils.storage import response_storage
from datetime import datetime
from src.views.debug import debug_views

debug_bp = Blueprint('debug', __name__, url_prefix='/debug')

@debug_bp.route('/')
def debug_panel():
    return debug_views.debug_panel_view()

@debug_bp.route('/test-connection')
def test_connection():
    return debug_views.test_connection_view()

@debug_bp.route('/api/fetch_graphql', methods=['POST'])
def fetch_graphql():
    return debug_views.fetch_graphql_view()

@debug_bp.route('/api/load_last_response')
def load_last_response():
    return debug_views.load_last_response_view()

@debug_bp.route('/api/test_neo4j')
def test_neo4j():
    return debug_views.test_neo4j_view()

@debug_bp.route('/api/import_last_response')
def import_last_response():
    return debug_views.import_last_response_view()
