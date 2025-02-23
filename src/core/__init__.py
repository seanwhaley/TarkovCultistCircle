"""Core functionality module with minimal essential components."""
from src.core.decorators import db_transaction, validate_form_data
from src.core.limiter import rate_limiter
from src.core.extensions import login_manager
from src.core.metrics import metrics_collector

__all__ = [
    'db_transaction',
    'validate_form_data',
    'rate_limiter',
    'login_manager',
    'metrics_collector'
]
