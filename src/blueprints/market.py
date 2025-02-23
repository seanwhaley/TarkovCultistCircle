from flask import Blueprint
from src.utils.rate_limit import rate_limit
from src.views.market import get_market_trends_view, get_market_stats_view

bp = Blueprint('market', __name__)

@bp.route('/trends')
@rate_limit(100, 3600)
def get_market_trends():
    return get_market_trends_view()

@bp.route('/statistics')
@rate_limit(100, 3600)
def get_market_statistics():
    return get_market_stats_view()
