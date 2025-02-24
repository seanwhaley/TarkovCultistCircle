"""Application initialization configuration."""
import logging
from flask import Flask
from typing import Dict

logger = logging.getLogger(__name__)

class RateLimitConfig:
    """Rate limiting configuration."""
    def __init__(self, app_config: Dict):
        self.enabled = app_config.get('RATE_LIMIT_ENABLED', True)
        self.default_limit = app_config.get('RATE_LIMIT_DEFAULT', 1000)
        self.default_window = app_config.get('RATE_LIMIT_WINDOW', 3600)

def init_rate_limiter(app: Flask) -> None:
    """Initialize rate limiting for the application."""
    if not app.config.get('RATE_LIMIT_ENABLED', True):
        logger.info("Rate limiting is disabled")
        return

    try:
        config = RateLimitConfig(app.config)
        app.config['RATE_LIMIT_CONFIG'] = config.__dict__
        logger.info("Rate limiting initialized with in-memory storage")
    except Exception as e:
        logger.error(f"Failed to initialize rate limiting: {str(e)}")
        raise

def get_route_limits(path: str, config: RateLimitConfig) -> tuple[int, int]:
    """Get rate limits for a specific route."""
    route_limits = {
        "/auth/register": (3, 3600),  # 3 requests per hour
        "/auth/login": (10, 60),      # 10 requests per minute
        "/items/price-override": (10, 60),  # 10 overrides per minute
        "/items/blacklist": (5, 60),       # 5 requests per minute
        "/items/lock": (5, 60),            # 5 requests per minute
        "/market/analytics": (100, 60),     # 100 requests per minute
        "/optimize/calculate": (20, 60),    # 20 calculations per minute
    }
    
    for prefix, limits in route_limits.items():
        if path.startswith(prefix):
            return limits
    
    return config.default_limit, config.default_window

def is_path_exempt(path: str) -> bool:
    """Check if a path is exempt from rate limiting."""
    exempt_paths = [
        "/static/",
        "/favicon.ico",
        "/health",
    ]
    return any(path.startswith(exempt) for exempt in exempt_paths)