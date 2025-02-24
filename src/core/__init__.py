"""Core module initialization."""
import uuid
import json
from datetime import datetime
from typing import Optional

from flask import current_app
from geventwebsocket import WebSocketError

from .cache import cache, cached, invalidate_cache
from .errors import register_error_handlers
from .limiter import rate_limit
from .tasks import task_manager, background_task
from .scheduler import SchedulerManager
from .websocket import ConnectionManager, MarketUpdate

# Initialize core components
websocket_manager = ConnectionManager()

__all__ = [
    'cache',
    'cached',
    'invalidate_cache',
    'register_error_handlers',
    'rate_limit',
    'task_manager',
    'background_task',
    'SchedulerManager',
    'websocket_manager',
    'MarketUpdate'
]
