# This file is required to make this directory a Python package.

from flask import Flask
from src.config import config
from src.application.app_factory import ApplicationFactory
from src.core.error_handlers import register_error_handlers

# Import necessary modules and functions to support app_factory
from .app_factory import ApplicationFactory

# Ensure the package is correctly initialized
__all__ = ['ApplicationFactory']
