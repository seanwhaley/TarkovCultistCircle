"""Authentication forms."""
from typing import Optional
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, ValidationError
from wtforms.validators import DataRequired, Length, EqualTo, Email

class LoginForm(FlaskForm):
    """User login form."""
    username = StringField('Username', validators=[
        DataRequired(message="Username is required"),
        Length(min=3, max=50, message="Username must be between 3 and 50 characters")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required")
    ])

class RegisterForm(FlaskForm):
    """User registration form."""
    username = StringField('Username', validators=[
        DataRequired(message="Username is required"),
        Length(min=3, max=50, message="Username must be between 3 and 50 characters")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required"),
        Length(min=8, message="Password must be at least 8 characters long")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your password"),
        EqualTo('password', message="Passwords must match")
    ])

class ChangePasswordForm(FlaskForm):
    """Password change form."""
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message="Current password is required")
    ])
    new_password = PasswordField('New Password', validators=[
        DataRequired(message="New password is required"),
        Length(min=8, message="Password must be at least 8 characters long")
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message="Please confirm your new password"),
        EqualTo('new_password', message="Passwords must match")
    ])
