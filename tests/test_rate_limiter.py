"""Integration tests for rate limiting system."""
import time
from unittest.mock import patch
from flask import Flask, jsonify
from src.core.limiter import InMemoryRateLimiter
from src.core.middleware.ratelimit import RateLimitMiddleware, rate_limit

def test_rate_limiter_middleware():
    """Test rate limiting middleware."""
    app = Flask(__name__)
    app.config['RATE_LIMIT_ENABLED'] = True
    app.config['RATE_LIMIT_DEFAULT'] = 2
    app.config['RATE_LIMIT_WINDOW'] = 1
    
    app.wsgi_app = RateLimitMiddleware(app.wsgi_app)
    
    @app.route('/test')
    def test_route():
        return jsonify({"status": "ok"})
    
    client = app.test_client()
    
    # First request should succeed
    response = client.get('/test')
    assert response.status_code == 200
    
    # Second request should succeed
    response = client.get('/test')
    assert response.status_code == 200
    
    # Third request should be rate limited
    response = client.get('/test')
    assert response.status_code == 429
    assert 'Retry-After' in response.headers
    
    # Wait for window to expire
    time.sleep(1.1)
    
    # Request after window should succeed
    response = client.get('/test')
    assert response.status_code == 200

def test_rate_limit_decorator():
    """Test rate limit decorator."""
    app = Flask(__name__)
    app.config['RATE_LIMIT_ENABLED'] = True
    app.config['RATE_LIMIT_DEFAULT'] = 2
    app.config['RATE_LIMIT_WINDOW'] = 1
    
    @app.route('/decorated')
    @rate_limit
    def decorated_route():
        return jsonify({"status": "ok"})
    
    client = app.test_client()
    
    # First request should succeed
    response = client.get('/decorated')
    assert response.status_code == 200
    
    # Second request should succeed
    response = client.get('/decorated')
    assert response.status_code == 200
    
    # Third request should be rate limited
    response = client.get('/decorated')
    assert response.status_code == 429
    
def test_disabled_rate_limiting():
    """Test behavior when rate limiting is disabled."""
    app = Flask(__name__)
    app.config['RATE_LIMIT_ENABLED'] = False
    
    app.wsgi_app = RateLimitMiddleware(app.wsgi_app)
    
    @app.route('/test')
    def test_route():
        return jsonify({"status": "ok"})
    
    client = app.test_client()
    
    # Multiple requests should succeed when disabled
    for _ in range(5):
        response = client.get('/test')
        assert response.status_code == 200

def test_exempt_paths():
    """Test that static and health check paths are exempt."""
    app = Flask(__name__)
    app.config['RATE_LIMIT_ENABLED'] = True
    app.config['RATE_LIMIT_DEFAULT'] = 1
    
    app.wsgi_app = RateLimitMiddleware(app.wsgi_app)
    
    client = app.test_client()
    
    # Static files should be exempt
    for _ in range(5):
        response = client.get('/static/test.css')
        assert response.status_code == 404  # 404 because file doesn't exist
        
    # Health check should be exempt
    for _ in range(5):
        response = client.get('/health')
        assert response.status_code == 404  # 404 because route doesn't exist