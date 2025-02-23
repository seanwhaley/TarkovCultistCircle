"""Flask extensions initialization."""
from typing import Any
from flask import Flask
from flask_limiter import Limiter
from flask_caching import Cache
from flask_login import LoginManager

limiter = Limiter()
cache = Cache()
login_manager = LoginManager()

def init_extensions(app: Flask) -> None:
    """Initialize Flask extensions."""
    cache.init_app(app)
    limiter.init_app(app)
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    from src.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id: str) -> Any:
        return User.query.get(int(user_id))
