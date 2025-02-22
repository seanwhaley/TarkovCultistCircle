# Standard library imports
import logging

# Third-party imports
from flask import Blueprint, current_app, jsonify, request
from flask_login import login_required

# Local imports
from core.graphql import GraphQLClient
from core.limiter import rate_limit
from services.item_service import ItemService

api_bp = Blueprint('api', __name__)

@api_bp.before_request
def before_request():
    if not current_app.config.get('API_ENABLED', True):
        return jsonify({'error': 'API is disabled'}), 503

@api_bp.route('/')
def get_status():
    """API status endpoint"""
    return jsonify({
        "status": "operational",
        "version": current_app.config.get('API_VERSION', 'v1')
    })

@api_bp.route('/items')
@login_required
@rate_limit({'default': (current_app.config.get('API_RATE_LIMIT', 1000), 3600)})
def get_items():
    try:
        service = ItemService()
        items = service.get_all_items()
        return jsonify(items)
    except Exception as e:
        logging.error(f"API error in get_items: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/refresh', methods=['POST'])
@login_required
@rate_limit({'default': (current_app.config.get('API_REFRESH_LIMIT', 20), 3600)})
def refresh_data():
    """
    Refresh data from the Tarkov API.

    Returns:
        JSON response indicating the success or failure of the data refresh.
    """
    try:
        client = GraphQLClient()
        result = client.fetch_items()
        # Process the result and update the database
        return jsonify({"success": True, "details": {"itemCount": len(result['data']['items'])}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Remove duplicate error handlers - now handled in errors.py
