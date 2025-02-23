from flask import Blueprint, render_template, redirect, url_for, request
from src.db import get_db

items_bp = Blueprint('items', __name__)

@items_bp.route('/items')
def items():
    db = get_db()
    try:
        items = db.query("MATCH (i:Item) RETURN i")
        return render_template('items.html', items=items)
    finally:
        db.close()

@items_bp.route('/price_override', methods=['POST'])
def price_override():
    item_id = request.form.get('item_id')
    price = request.form.get('price')
    return redirect(url_for('items.items'))

@items_bp.route('/blacklist_item', methods=['POST'])
def blacklist_item():
    item_id = request.form.get('item_id')
    duration = request.form.get('duration')
    return redirect(url_for('items.items'))

@items_bp.route('/lock_item', methods=['POST'])
def lock_item():
    item_id = request.form.get('item_id')
    duration = request.form.get('duration')
    return redirect(url_for('items.items'))
