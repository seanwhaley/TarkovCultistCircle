import unittest
from typing import Generator, Optional
import pytest
from flask import Flask
from src.forms.auth import LoginForm, RegistrationForm
from src.application.app_factory import ApplicationFactory
from src.core.db import Neo4jConnection
from src.config import Config

@pytest.fixture
def app() -> Flask:
    app = ApplicationFactory.create_app(Config)
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test_secret',
        'WTF_CSRF_ENABLED': False,
        'NEO4J_URI': 'bolt://localhost:7687',
        'NEO4J_USER': 'neo4j',
        'NEO4J_PASSWORD': 'test'
    })
    return app

@pytest.fixture
def db(app: Flask) -> Generator[Neo4jConnection, None, None]:
    db = Neo4jConnection(
        uri=app.config['NEO4J_URI'],
        user=app.config['NEO4J_USER'],
        password=app.config['NEO4J_PASSWORD'],
        database='neo4j'
    )
    yield db
    db.close()

class TestForms(unittest.TestCase):
    def setUp(self) -> None:
        self.app = ApplicationFactory.create_app()
        self.app.config['SECRET_KEY'] = 'mysecret'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self) -> None:
        if self.app_context:
            self.app_context.pop()

    def test_login_form_valid(self) -> None:
        form = LoginForm(data={'username': 'testuser', 'password': 'password'})
        self.assertTrue(form.validate())

    def test_login_form_invalid_username(self) -> None:
        form = LoginForm(data={'username': '', 'password': 'password'})
        self.assertFalse(form.validate())

    def test_login_form_invalid_password(self) -> None:
        form = LoginForm(data={'username': 'testuser', 'password': ''})
        self.assertFalse(form.validate())

    def test_registration_form_valid(self) -> None:
        form = RegistrationForm(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password',
            'confirm_password': 'password'
        })
        self.assertTrue(form.validate())

    def test_registration_form_invalid_username(self) -> None:
        form = RegistrationForm(data={
            'username': '',
            'email': 'test@example.com',
            'password': 'password',
            'confirm_password': 'password'
        })
        self.assertFalse(form.validate())

    def test_registration_form_invalid_email(self) -> None:
        form = RegistrationForm(data={
            'username': 'testuser',
            'email': 'invalidemail',
            'password': 'password',
            'confirm_password': 'password'
        })
        self.assertFalse(form.validate())

    def test_registration_form_invalid_password(self) -> None:
        form = RegistrationForm(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '',
            'confirm_password': 'password'
        })
        self.assertFalse(form.validate())

    def test_registration_form_password_mismatch(self) -> None:
        form = RegistrationForm(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password',
            'confirm_password': 'differentpassword'
        })
        self.assertFalse(form.validate())

if __name__ == '__main__':
    unittest.main()
