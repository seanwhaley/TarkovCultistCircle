import unittest
from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=35)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class TestForms(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'mysecret'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_login_form_valid(self):
        form = LoginForm(username='testuser', password='password')
        self.assertTrue(form.validate())

    def test_login_form_invalid_username(self):
        form = LoginForm(username='', password='password')
        self.assertFalse(form.validate())

    def test_login_form_invalid_password(self):
        form = LoginForm(username='testuser', password='')
        self.assertFalse(form.validate())

    def test_registration_form_valid(self):
        form = RegistrationForm(username='testuser', email='test@example.com', password='password', confirm_password='password')
        self.assertTrue(form.validate())

    def test_registration_form_invalid_username(self):
        form = RegistrationForm(username='', email='test@example.com', password='password', confirm_password='password')
        self.assertFalse(form.validate())

    def test_registration_form_invalid_email(self):
        form = RegistrationForm(username='testuser', email='invalidemail', password='password', confirm_password='password')
        self.assertFalse(form.validate())

    def test_registration_form_invalid_password(self):
        form = RegistrationForm(username='testuser', email='test@example.com', password='', confirm_password='password')
        self.assertFalse(form.validate())

    def test_registration_form_password_mismatch(self):
        form = RegistrationForm(username='testuser', email='test@example.com', password='password', confirm_password='differentpassword')
        self.assertFalse(form.validate())

if __name__ == '__main__':
    unittest.main()
