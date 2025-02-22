from flask import Blueprint
from src.blueprints import *

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Register routes
admin_bp.add_url_rule('/dashboard', view_func=dashboard, methods=['GET'])
admin_bp.add_url_rule('/users', view_func=manage_users, methods=['GET', 'POST'])
admin_bp.add_url_rule('/system-status', view_func=system_status, methods=['GET'])

__all__ = ['admin_bp']
