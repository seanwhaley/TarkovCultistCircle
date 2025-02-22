import os
from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        config = current_app.config
        auth_header = request.headers.get(config['AUTH_HEADER_NAME'])
        if not auth_header:
            return jsonify({'error': 'Missing authorization header'}), 401

        auth_type = config['AUTH_HEADER_TYPE']
        if not auth_header.startswith(auth_type):
            return jsonify({'error': 'Invalid authorization type'}), 401

        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401

    return decorated

def initialize_auth(app):
    """JWT configuration is already loaded from config.py"""
    pass  # Remove redundant configuration as it's already in app.config
