from flask import jsonify
from src.db import get_db

def get_items_view():
    """View function for getting all items"""
    db = get_db()
    items = db.query("MATCH (i:Item) RETURN i")
    return jsonify([dict(item['i']) for item in items])

def get_item_view(item_id):
    """View function for getting a single item"""
    db = get_db()
    item = db.query("MATCH (i:Item {id: $id}) RETURN i", {'id': item_id})
    return jsonify(dict(item[0]['i'])) if item else ('Not found', 404)

def get_price_history_view(item_id):
    """View function for getting item price history"""
    db = get_db()
    history = db.get_item_price_history(item_id)
    return jsonify(history)
