from flask import Blueprint, render_template
from src.utils.rate_limit import rate_limit
from src.db import get_db

bp = Blueprint('items', __name__)

@bp.route('/')
@rate_limit(100, 3600)  # 100 requests per hour
def get_items():
    db = get_db()
    # ...existing implementation...

# ...existing routes...
