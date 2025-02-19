from flask import Blueprint, jsonify, current_app

api_bp = Blueprint('api', __name__)

@api_bp.route('/status')
def status():
    return jsonify({
        'status': 'ok',
        'database': current_app.db.test_connection()
    })
