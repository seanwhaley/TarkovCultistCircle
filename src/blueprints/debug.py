"""Debug and monitoring functionality."""
import logging
import platform
import sys
import os
import json
from functools import wraps
from typing import Dict, Any

# Third-party imports
from flask import Blueprint, current_app, abort, render_template, jsonify, request

# Local imports
from core.database import get_db
from core.security import admin_required
from core.health import health_check
from core.metrics import metrics_collector
from src.core.config import Config
from src.database.neo4j import Neo4jDB
from src.utils.prompt_storage import PromptResponseStorage

logger = logging.getLogger(__name__)
debug_bp = Blueprint('debug', __name__)

RESPONSES_DIR = "storage/responses"

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

@debug_bp.route('/ai-prompts')
@admin_required
@debug_only
def view_ai_prompts():
    """View stored AI prompts and responses."""
    try:
        # Get JSON files from storage directory
        file_responses = {}
        if os.path.exists(RESPONSES_DIR):
            for filename in os.listdir(RESPONSES_DIR):
                if filename.endswith('.json'):
                    filepath = os.path.join(RESPONSES_DIR, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        file_responses[filename] = json.load(f)

        # Get Neo4j responses
        db = Neo4jDB()
        storage = PromptResponseStorage(db)
        
        analysis_prompts = []
        action_prompts = []
        
        raw_prompts = db.get_prompt_responses()
        for prompt in raw_prompts:
            if prompt.get('type') == 'analysis' and storage.validate_report_format(prompt):
                analysis_prompts.append(prompt)
            elif prompt.get('type') == 'action_plan':
                action_prompts.append(prompt)
        
        return render_template('pages/debug/ai_prompts.html',
                            file_responses=file_responses,
                            analysis_prompts=analysis_prompts,
                            action_prompts=action_prompts,
                            Config=Config)
    except Exception as e:
        logger.error(f"Error fetching AI prompts: {str(e)}")
        return jsonify({'error': str(e)}), 500

@debug_bp.route('/import-prompt', methods=['POST'])
@admin_required
@debug_only
def import_prompt():
    """Import a prompt response from JSON file to Neo4j."""
    try:
        filename = request.json.get('filename')
        if not filename:
            return jsonify({'success': False, 'error': 'Filename is required'}), 400

        filepath = os.path.join(RESPONSES_DIR, filename)
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File not found'}), 404

        # Read JSON file
        with open(filepath, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Import to Neo4j
        db = Neo4jDB()
        storage = PromptResponseStorage(db)
        prompt_id = storage.import_to_neo4j(json_data)
        
        # Delete the file after successful import
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': 'Successfully imported to Neo4j',
            'prompt_id': prompt_id
        })
    except Exception as e:
        logger.error(f"Error importing prompt: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@debug_bp.route('/delete-prompt-file', methods=['POST'])
@admin_required
@debug_only
def delete_prompt_file():
    """Delete a prompt response JSON file."""
    try:
        filename = request.json.get('filename')
        if not filename:
            return jsonify({'success': False, 'error': 'Filename is required'}), 400

        filepath = os.path.join(RESPONSES_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': 'File deleted successfully'
        })
    except Exception as e:
        logger.error(f"Error deleting prompt file: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@debug_bp.route('/view-prompt/<prompt_id>')
@admin_required
@debug_only
def view_prompt(prompt_id):
    """Get details of a specific prompt from Neo4j."""
    try:
        db = Neo4jDB()
        storage = PromptResponseStorage(db)
        prompt = storage.get_prompt_by_id(prompt_id)
        
        if not prompt:
            return jsonify({'error': 'Prompt not found'}), 404
            
        return jsonify(prompt)
    except Exception as e:
        logger.error(f"Error fetching prompt details: {str(e)}")
        return jsonify({'error': str(e)}), 500

def _check_neo4j_connection() -> str:
    """Check Neo4j connection status."""
    try:
        db = get_db()
        db.test_connection()
        return "Connected"
    except Exception as e:
        logging.error(f"Neo4j connection error: {str(e)}")
        return f"Error: {str(e)}"
