from flask import Blueprint, render_template, request, jsonify, flash
from src.core.graphql import GraphQLClient
from src.db import get_db
from src.models import Item

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/debug')
def debug():
    """
    Debug page route.

    Returns:
        Rendered debug page template.
    """
    return render_template('debug.html')

@debug_bp.route('/debug/graphql', methods=['POST'])
def test_graphql():
    """
    Test GraphQL query.

    Returns:
        JSON response with query result.
    """
    query = request.json.get('query')
    client = GraphQLClient()
    try:
        result = client.execute(query)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@debug_bp.route('/debug/neo4j', methods=['POST'])
def test_neo4j():
    """
    Test Neo4j query.

    Returns:
        JSON response with query result.
    """
    query = request.json.get('query')
    db = get_db()
    try:
        result = db.query(query)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@debug_bp.route('/debug/import_graphql', methods=['POST'])
def import_graphql():
    """
    Import GraphQL data into Neo4j.

    Returns:
        JSON response with import status.
    """
    items = request.json.get('items', [])
    db = get_db()
    try:
        for item_data in items:
            item = Item.nodes.get_or_none(uid=item_data['id'])
            if not item:
                item = Item(uid=item_data['id'])
            item.name = item_data['name']
            item.base_price = item_data['basePrice']
            item.last_low_price = item_data.get('lastLowPrice')
            item.avg_24h_price = item_data.get('avg24hPrice')
            item.updated_at = item_data['updated']
            item.save()
        return jsonify({"message": "Data imported successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
