# This file is required to make this directory a Python package.

from flask import Flask
from src.config import config
from src.application.app_factory import ApplicationFactory
from src.core.error_handlers import register_error_handlers

# Ensure the package is correctly initialized
__all__ = ['ApplicationFactory']
