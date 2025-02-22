# Standard library imports
import logging
from functools import wraps
from datetime import datetime, timedelta

# Third-party imports
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for, Response, jsonify, session
from flask_login import current_user, login_required, login_user, logout_user  # type: ignore
from werkzeug.security import check_password_hash
import jwt

# Local imports
from src.core.limiter import rate_limit
from src.forms.auth import ChangePasswordForm, LoginForm, RegisterForm  # type: ignore
from src.services.auth_service import AuthService
from src.services.exceptions import AuthError, ValidationError  # type: ignore
from src.models import User

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('admin_token')
        
        if not token:
            return jsonify({'message': 'Admin token is missing'}), 401

        try:
            jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return f(*args, **kwargs)
        except:
            return jsonify({'message': 'Invalid admin token'}), 401

    return decorated

@auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if not data or 'password' not in data:
        return jsonify({'message': 'Password is required'}), 400

    admin_password_hash = current_app.config['ADMIN_PASSWORD_HASH']
    if check_password_hash(admin_password_hash, data['password']):
        token = jwt.encode({
            'admin': True,
            'exp': datetime.now(datetime.timezone.utc) + timedelta(days=1)
        }, current_app.config['SECRET_KEY'])
        
        response = jsonify({'message': 'Login successful'})
        response.set_cookie('admin_token', token, httponly=True, secure=True)
        return response
    
    return jsonify({'message': 'Invalid password'}), 401

@auth_bp.route('/admin/logout')
def admin_logout() -> Response:
    response = jsonify({'message': 'Logged out'})
    response.delete_cookie('admin_token')
    return response

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
            session['user_id'] = user.id
            flash('Login successful', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """
    Logout route.

    Returns:
        Redirects to the home page.
    """
    session.pop('user_id', None)
    flash('Logout successful', 'success')
    return redirect(url_for('main.home'))

@auth_bp.route('/register', methods=['GET', 'POST'])
@rate_limit({'default': (int(current_app.config.get('AUTH_REGISTER_LIMIT', 3)), 3600)})
def register() -> Response:
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        
        form = RegisterForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                user = auth_service.create_user(
                    username=form.username.data,
                    password=form.password.data
                )
                login_user(user)
                flash('Registration successful!', 'success')
                return redirect(url_for('main.index'))
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f"{field}: {error}", 'error')
                return Response(render_template('pages/auth/register.html', form=form), status=400)
            
        return Response(render_template('pages/auth/register.html', form=form))
    except ValidationError as e:
        flash(str(e), 'error')
        return render_template('pages/auth/register.html', form=form), 400
    except Exception as e:
        logging.error(f"Registration error: {str(e)}")
        flash("An error occurred during registration", "error")
        return Response(render_template('pages/auth/register.html', form=form), status=500)

@auth_bp.route('/profile')
@login_required
def profile() -> Response:
    return Response(render_template('pages/auth/profile.html'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password() -> Response:
    form = ChangePasswordForm()
    if form.validate_on_submit():
        try:
            auth_service.change_password(current_user.id, form.new_password.data)
            flash('Password changed successfully.', 'success')
            return redirect(url_for('auth.profile'))  # type: ignore
        except AuthError as e:
            flash(str(e), 'error')
    return Response(render_template('pages/auth/change_password.html', form=form))