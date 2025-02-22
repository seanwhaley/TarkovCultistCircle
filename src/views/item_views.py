from typing import Dict, List, Any, Optional, cast
from flask import jsonify, request
from src.database import Neo4jDB
from src.services.item_service import ItemService
from src.services.exceptions import ValidationError, ItemNotFoundError
from src.types.flask import ResponseValue
from src.types import ItemResponse, PriceHistoryEntry

def get_items_view() -> ResponseValue:
    """Get all items"""
    service = ItemService()
    try:
        items: List[ItemResponse] = service.get_all_items()
        return jsonify({"items": items}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_item_view(item_id: str) -> ResponseValue:
    """Get specific item by ID"""
    service = ItemService()
    try:
        item: Optional[ItemResponse] = service.get_item(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404
        return jsonify(item), 200
    except ItemNotFoundError:
        return jsonify({"error": "Item not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def update_item_price_view(item_id: str) -> ResponseValue:
    """Update item price"""
    service = ItemService()
    try:
        data: Optional[Dict[str, Any]] = request.get_json()
        if not data or 'price' not in data:
            return jsonify({"error": "Price is required"}), 400
            
        price: float = float(data['price'])
        service.override_price(item_id, price)
        return jsonify({"message": "Price updated successfully"}), 200
    except (ValueError, ValidationError) as e:
        return jsonify({"error": str(e)}), 400
    except ItemNotFoundError:
        return jsonify({"error": "Item not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_price_history_view(item_id: str) -> ResponseValue:
    """Get price history for an item"""
    service = ItemService()
    try:
        days: int = int(request.args.get('days', '30'))
        history: List[PriceHistoryEntry] = service.get_price_history(item_id, days)
        return jsonify({"history": history}), 200
    except ValueError:
        return jsonify({"error": "Invalid days parameter"}), 400
    except ItemNotFoundError:
        return jsonify({"error": "Item not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def blacklist_item_view(item_id: str) -> ResponseValue:
    """Blacklist an item"""
    service = ItemService()
    try:
        data: Optional[Dict[str, Any]] = request.get_json()
        if not data or 'duration' not in data:
            return jsonify({"error": "Duration is required"}), 400
            
        duration: int = int(data['duration'])
        service.blacklist_item(item_id, duration)
        return jsonify({"message": "Item blacklisted successfully"}), 200
    except ValueError:
        return jsonify({"error": "Invalid duration value"}), 400
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except ItemNotFoundError:
        return jsonify({"error": "Item not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
