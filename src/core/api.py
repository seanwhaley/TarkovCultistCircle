from functools import wraps
from flask import current_app, Blueprint, abort
import logging

logger = logging.getLogger(__name__)

def api_blueprint(name: str) -> Blueprint:
    """Create a blueprint with proper API version prefix"""
    if not name:
        raise ValueError("Blueprint name cannot be empty")
        
    try:
        prefix = current_app.config.get('API_PREFIX', '/api')
        version = current_app.config.get('API_VERSION', 'v1')
        return Blueprint(name, __name__, url_prefix=f"{prefix}/{version}/{name}")
    except Exception as e:
        logger.error(f"Failed to create API blueprint {name}: {str(e)}")
        raise

def require_api(f):
    """Decorator to check if API is enabled"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            if not current_app.config.get('API_ENABLED', True):
                logger.warning("API access attempted while disabled")
                return {'error': 'API is disabled'}, 503
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"API access error: {str(e)}")
            return {'error': 'Internal server error'}, 500
    return decorated
