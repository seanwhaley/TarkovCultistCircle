from src.application.app_factory import ApplicationFactory
from src.config import config

create_app = ApplicationFactory.create_app
run_app = ApplicationFactory.run_app

__all__ = ['create_app', 'run_app', 'config']