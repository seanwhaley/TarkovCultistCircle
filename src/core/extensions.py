"""Essential Flask extensions initialization."""
from typing import Any
from flask import Flask
from flask_login import LoginManager

# Initialize login manager
login_manager = LoginManager()

def init_extensions(app: Flask) -> None:
    """Initialize Flask extensions."""
    # Configure and initialize login manager with secure defaults
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'
    
    from src.models.user import User
    
    @login_manager.user_loader
    def load_user(user_id: str) -> Any:
        return User.query.get(int(user_id))
