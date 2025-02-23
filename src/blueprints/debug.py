"""Debug and monitoring functionality."""
# Standard library imports
import logging
import platform
import sys
from functools import wraps
from typing import Dict, Any

# Third-party imports
from flask import Blueprint, current_app, abort, render_template, jsonify

# Local imports
from core.database import get_db
from core.security import admin_required
from core.health import health_check
from core.metrics import metrics_collector

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
    """Debug dashboard."""
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
    """Display non-sensitive configuration."""
    safe_config = {k: v for k, v in current_app.config.items() 
                  if not k.startswith('_') and k.isupper()}
    return render_template('pages/debug/config.html', config=safe_config)

@debug_bp.route('/routes')
@admin_required
@debug_only
def debug_routes() -> str:
    """Display all application routes."""
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
    """Display non-sensitive environment configuration."""
    excluded_keys = current_app.config.get('DEBUG_EXCLUDED_CONFIG_KEYS', 
                                         ['KEY', 'PASSWORD', 'SECRET', 'TOKEN', 'CREDENTIALS'])
    safe_config = {
        k: v for k, v in current_app.config.items()
        if not any(secret.lower() in k.lower() for secret in excluded_keys)
        and not k.startswith('_')
    }
    return render_template('pages/debug/environment.html', config=safe_config)

@debug_bp.route('/health')
@admin_required
@debug_only
async def system_health():
    """Get complete system health status."""
    return jsonify(await health_check.get_health_status())

@debug_bp.route('/health/<component>')
@admin_required
@debug_only
async def component_health(component: str):
    """Get health status for a specific component."""
    try:
        status = await health_check.get_component_status(component)
        return jsonify(status)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@debug_bp.route('/metrics')
@admin_required
@debug_only
async def system_metrics():
    """Get system metrics for the last 5 minutes."""
    request_stats = await metrics_collector.get_request_stats(minutes=5)
    performance_stats = await metrics_collector.get_performance_stats(minutes=5)
    return jsonify({
        'requests': request_stats,
        'performance': performance_stats
    })

def _check_neo4j_connection() -> str:
    """Check Neo4j connection status."""
    try:
        db = get_db()
        db.test_connection()
        return "Connected"
    except Exception as e:
        logging.error(f"Neo4j connection error: {str(e)}")
        return f"Error: {str(e)}"
