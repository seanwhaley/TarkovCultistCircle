# Standard library imports
import logging

# Third-party imports
from flask import Blueprint, current_app, jsonify, render_template, request

# Local imports
from src.core.neo4j import Neo4jClient
from src.services.exceptions import OptimizationError
from src.services.data_service import DataService
from src.blueprints.auth import admin_required

optimizer_bp = Blueprint('optimizer', __name__)
data_service = DataService()

@optimizer_bp.route('/')
def index():
    """Main optimization interface"""
    config = {
        'max_items': current_app.config.get('OPTIMIZER_MAX_ITEMS', 5),
        'min_price': current_app.config.get('OPTIMIZER_MIN_PRICE', 400000),
    }
    return render_template('optimizer/index.html', config=config)

@optimizer_bp.route('/optimize', methods=['POST'])
def optimize():
    """Find optimal item combinations"""
    try:
        data = request.get_json()
        min_price = float(data.get('minPrice', 400000))
        max_items = min(int(data.get('maxItems', 5)), 5)
        
        combinations = data_service.optimize_combinations(
            min_price=min_price,
            max_items=max_items
        )
            
        return jsonify({
            'success': True,
            'combinations': combinations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@optimizer_bp.route('/price-override', methods=['POST'])
def set_price_override():
    """Override item price"""
    try:
        data = request.get_json()
        item_id = data['itemId']
        price = float(data['price'])
        duration = data.get('duration')
        
        data_service.set_price_override(item_id, price, duration)
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@optimizer_bp.route('/history', methods=['GET', 'POST'])
def history():
    """Get or save combination history"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            combination_id = data_service.save_combination(
                items=data['items'],
                total_price=data['totalPrice']
            )
            return jsonify({
                'success': True,
                'id': combination_id
            })
        else:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            history_data = data_service.get_history(page, per_page)
            return jsonify({
                'success': True,
                'history': history_data
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@optimizer_bp.route('/history/<combination_id>', methods=['DELETE'])
@admin_required
def delete_history_entry(combination_id):
    """Delete a historical combination (admin only)"""
    try:
        data_service.delete_combination(combination_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@optimizer_bp.route('/blacklist', methods=['POST'])
def set_blacklist():
    """Blacklist an item"""
    try:
        data = request.get_json()
        item_id = data['itemId']
        blacklisted = bool(data['blacklisted'])
        duration = data.get('duration')
        
        data_service.set_blacklist(item_id, blacklisted, duration)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@optimizer_bp.route('/lock', methods=['POST'])
def set_lock():
    """Lock an item"""
    try:
        data = request.get_json()
        item_id = data['itemId']
        locked = bool(data['locked'])
        duration = data.get('duration')
        
        data_service.set_lock(item_id, locked, duration)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@optimizer_bp.route('/refresh', methods=['POST'])
def refresh_data():
    """Refresh item data from Tarkov.dev API"""
    try:
        result = data_service.fetch_and_store_items()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
