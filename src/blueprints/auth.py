from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    return "Login Page"

@auth_bp.route('/logout')
def logout():
    return "Logout Page"
```
# This file can be safely deleted.
