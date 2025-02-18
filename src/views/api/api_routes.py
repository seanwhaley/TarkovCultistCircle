from flask import Blueprint, jsonify, current_app
from src.core.graphql import GraphQLClient

api_bp = Blueprint('api', __name__)

@api_bp.route('/status')
def status():
    return jsonify({
        'status': 'ok',
        'database': current_app.db.test_connection()
    })

@api_bp.route('/refresh-data', methods=['POST'])
def refresh_data():
    try:
        client = GraphQLClient()
        result = client.execute_query()  # Uses default query from Config
        current_app.db.save_items(result.get('data', {}).get('items', []))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/items')
def get_items():
    """Get all items from database"""
    try:
        with current_app.db.get_session() as session:
            items = session.run("MATCH (i:Item) RETURN i")
            return jsonify({'items': [dict(item['i']) for item in items]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
