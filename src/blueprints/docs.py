from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash, session
from src.config.tarkov_schema import save_schema_documentation
from src.core.graphql import GraphQLClient
from src.models import Item

docs_bp = Blueprint('docs', __name__)

@docs_bp.route('/update_docs', methods=['GET'])
def update_docs():
    try:
        save_schema_documentation()
        return jsonify({"message": "API schema documentation updated successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@docs_bp.route('/fetch_api_data', methods=['POST'])
def fetch_api_data():
    try:
        client = GraphQLClient()
        result = client.fetch_items()
        session['api_data'] = result['data']['items']
        flash("API data fetched successfully.", "success")
    except Exception as e:
        flash(f"Error fetching API data: {str(e)}", "danger")
    return redirect(url_for('docs.update_database'))

@docs_bp.route('/push_to_database', methods=['POST'])
def push_to_database():
    try:
        items = session.get('api_data', [])
        if not items:
            flash("No API data available to push to the database.", "warning")
            return redirect(url_for('docs.update_database'))
        
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
        
        flash("Database updated successfully.", "success")
    except Exception as e:
        flash(f"Error updating database: {str(e)}", "danger")
    return redirect(url_for('docs.update_database'))

@docs_bp.route('/update_database', methods=['GET', 'POST'])
def update_database():
    return render_template('update.html')
