# Standard library imports
import logging
import platform
import sys
from functools import wraps
from typing import Dict, Any

# Third-party imports
from flask import Blueprint, current_app, abort, render_template

# Local imports
from core.database import get_db
from core.security import admin_required

debug_bp = Blueprint('debug', __name__)

def debug_only(f):
    """Decorator to ensure route only works in debug mode"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_app.config.get('DEBUG', False) or \
           not current_app.config.get('ENABLE_DEBUG_ROUTES', False):
            abort(404)
        return f(*args, **kwargs)
    return decorated_function

@debug_bp.route('/')
@admin_required
@debug_only
def index() -> str:
    info = {
        'python_version': sys.version,
        'platform': platform.platform(),
        'environment': current_app.config['FLASK_ENV'],
        'debug_mode': current_app.config['DEBUG'],
        'neo4j_status': _check_neo4j_connection()
    }
    return render_template('pages/debug/index.html', info=info)

@debug_bp.route('/config')
@admin_required
@debug_only
def debug_config() -> str:
    safe_config = {k: v for k, v in current_app.config.items() 
                  if not k.startswith('_') and k.isupper()}
    return render_template('pages/debug/config.html', config=safe_config)

@debug_bp.route('/routes')
@admin_required
@debug_only
def debug_routes() -> str:
    routes = []
    for rule in current_app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': rule.rule
        })
    return render_template('pages/debug/routes.html', routes=routes)

@debug_bp.route('/environment')
@admin_required
@debug_only
def environment() -> str:
    """Display non-sensitive environment configuration"""
    excluded_keys = current_app.config.get('DEBUG_EXCLUDED_CONFIG_KEYS', 
                                         ['KEY', 'PASSWORD', 'SECRET', 'TOKEN', 'CREDENTIALS'])
    safe_config = {
        k: v for k, v in current_app.config.items()
        if not any(secret.lower() in k.lower() for secret in excluded_keys)
        and not k.startswith('_')
    }
    return render_template('pages/debug/environment.html', config=safe_config)

def _check_neo4j_connection() -> str:
    """Check Neo4j connection status"""
    try:
        db = get_db()
        db.test_connection()
        return "Connected"
    except Exception as e:
        logging.error(f"Neo4j connection error: {str(e)}")
        return f"Error: {str(e)}"
