from flask import Blueprint, jsonify, request
from src.core.graphql import GraphQLClient

api_bp = Blueprint('api', __name__)
"""
Blueprint for the API routes.

Attributes:
    api_bp (Blueprint): The API blueprint.
"""

@api_bp.route('/api/', methods=['GET'])
def get_data():
    """
    Retrieve the operational status of the API.

    Returns:
        JSON response indicating the operational status.
    """
    return jsonify({"status": "operational"})

@api_bp.route('/api/status', methods=['GET'])
def get_status():
    """
    Retrieve the database connection status.

    Returns:
        JSON response indicating the database connection status.
    """
    return jsonify({"status": "connected"})

@api_bp.route('/api/refresh_data', methods=['POST'])
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
        # ...existing code...
        return jsonify({"success": True, "details": {"itemCount": len(result['data']['items'])}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
