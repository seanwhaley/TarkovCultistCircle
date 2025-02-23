from typing import Tuple, Dict, Any, Optional, cast
import logging
from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required
from werkzeug.wrappers.response import Response as WerkzeugResponse

from src.core.cache import cached
from src.core.limiter import rate_limit
from src.core.decorators import db_transaction, validate_form_data
from src.services.exceptions import DatabaseError, ItemNotFoundError, ValidationError
from src.services.item_service import ItemService
from src.types.responses import (
    ResponseType, PaginatedResponse, ItemResponse, 
    ErrorResponse, SuccessResponse
)

bp = Blueprint('items', __name__)
logger = logging.getLogger(__name__)

# Use singleton pattern for service
_item_service: Optional[ItemService] = None

def get_item_service() -> ItemService:
    global _item_service
    if _item_service is None:
        _item_service = ItemService()
    return _item_service

@bp.route('/')
@cached(timeout=lambda: current_app.config['CACHE_DEFAULT_TIMEOUT'])
def index() -> ResponseType:
    try:
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['ITEMS_PER_PAGE']
        search = request.args.get('q', '')
        sort = request.args.get('sort', 'name')
        filter_type = request.args.get('filter', 'all')
        
        items, pagination = get_item_service().get_items_paginated(
            page=page,
            per_page=per_page,
            search=search,
            sort=sort,
            filter_type=filter_type
        )
        
        return render_template(
            'pages/items/index.html',
            items=items,
            pagination=pagination
        )
    except Exception as e:
        logger.error("Error in items index", exc_info=e)
        flash("Error loading items", "error")
        return render_template('pages/errors/500.html'), 500

@bp.route('/<item_id>')
@cached(timeout=60)
def detail(item_id: str) -> ResponseType:
    try:
        item = get_item_service().get_item(item_id)
        return render_template('pages/items/detail.html', item=item)
    except Exception as e:
        current_app.logger.error(f"Error in item detail: {str(e)}")
        raise

@bp.route('/price-override', methods=['POST'])
@login_required
@rate_limit({'default': (10, 60)})  # 10 overrides per minute
@db_transaction
@validate_form_data(['item_id', 'price'])
def price_override() -> ResponseType:
    try:
        item_id = cast(str, request.form['item_id'])
        price = float(request.form['price'])
        
        get_item_service().override_price(item_id, price)
        
        response: SuccessResponse = {
            "message": "Price override successful",
            "data": None
        }
        return jsonify(response)
        
    except ValidationError as e:
        error: ErrorResponse = {
            "error": str(e),
            "details": None
        }
        return jsonify(error), 400
    except Exception as e:
        logger.error("Price override error", exc_info=e)
        error: ErrorResponse = {
            "error": "Internal server error",
            "details": None
        }
        return jsonify(error), 500

@bp.route('/blacklist_item', methods=['POST'])
@rate_limit({'default': (5, 60)})  # 5 requests per minute
def blacklist_item() -> ResponseType:
    item_id = request.form.get('item_id')
    duration = request.form.get('duration')
    
    try:
        get_item_service().blacklist_item(item_id, duration)
        flash("Item blacklisted successfully", "success")
    except ValidationError as e:
        flash(str(e), "danger")
    except (DatabaseError, ItemNotFoundError) as e:
        flash(str(e), "danger")
    except Exception as e:
        current_app.logger.error(f"Error in blacklist item: {str(e)}")
        flash("An unexpected error occurred", "danger")
    
    return redirect(url_for('items.index'))

@bp.route('/lock_item', methods=['POST'])
@rate_limit({'default': (5, 60)})  # 5 requests per minute
def lock_item() -> ResponseType:
    item_id = request.form.get('item_id')
    duration = request.form.get('duration')
    
    try:
        get_item_service().lock_item(item_id, duration)
        flash("Item locked successfully", "success")
    except ValidationError as e:
        flash(str(e), "danger")
    except (DatabaseError, ItemNotFoundError) as e:
        flash(str(e), "danger")
    except Exception as e:
        current_app.logger.error(f"Error in lock item: {str(e)}")
        flash("An unexpected error occurred", "danger")
    
    return redirect(url_for('items.index'))

@bp.errorhandler(404)
def not_found_error(error) -> Tuple[str, int]:
    return render_template('pages/errors/404.html'), 404

@bp.errorhandler(500)
def internal_error(error) -> Tuple[str, int]:
    return render_template('pages/errors/500.html'), 500
