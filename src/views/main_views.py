from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """
    Home page route.

    Returns:
        Rendered home page template.
    """
    return render_template('home.html')

@main_bp.route('/debug')
def debug():
    """
    Debug page route.

    Returns:
        Rendered debug page template.
    """
    return render_template('debug.html')
