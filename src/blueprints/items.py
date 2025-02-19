from flask import Blueprint, render_template, current_app, request, jsonify
from http import HTTPStatus
from typing import Union, Dict, Any
from src.core.responses import success_response, error_response
from src.services.factory import ServiceFactory

items_bp = Blueprint('items', __name__, url_prefix='/items')

@items_bp.route('/')
def items_index() -> Union[str, tuple]:
    """Items main page"""
    try:
        return render_template('items/index.html')
    except Exception as e:
        current_app.logger.error(f"Error rendering items: {str(e)}")
        return error_response("Failed to render page", HTTPStatus.INTERNAL_SERVER_ERROR)

@items_bp.route('/api/list')
def list_items() -> Dict[str, Any]:
    """API endpoint to list items"""
    try:
        item_service = ServiceFactory.create_item_service()
        items = item_service.get_all_items()
        return success_response({"items": items})
    except Exception as e:
        current_app.logger.error(f"Error listing items: {str(e)}")
        return error_response("Failed to list items", HTTPStatus.INTERNAL_SERVER_ERROR)
