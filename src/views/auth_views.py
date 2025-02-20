from flask import Blueprint, render_template, redirect, url_for, request, flash
from src.models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login page route.

    Returns:
        Rendered login page template or redirects to the home page.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.nodes.get_or_none(username=username)
        if user and user.check_password(password):
            flash('Login successful', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """
    Logout route.

    Returns:
        Redirects to the home page.
    """
    # Implement logout logic
    flash('Logout successful', 'success')
    return redirect(url_for('main.home'))
