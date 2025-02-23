from flask import Blueprint, jsonify, render_template, request
from src.services.data_service import DataService
from src.blueprints.auth import admin_required

history_bp = Blueprint('history', __name__)
data_service = DataService()

@history_bp.route('/')
def index():
    """Show combination history page"""
    return render_template('optimizer/history.html')

@history_bp.route('/combinations')
def get_combinations():
    """Get paginated combination history"""
    try:
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

@history_bp.route('/combinations/<combination_id>', methods=['DELETE'])
@admin_required
def delete_combination(combination_id):
    """Delete a historical combination (admin only)"""
    try:
        data_service.delete_combination(combination_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400