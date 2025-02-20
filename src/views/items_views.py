from flask import Blueprint, render_template, redirect, url_for, request, flash
from src.db import get_db

items_bp = Blueprint('items', __name__)

@items_bp.route('/items')
def items():
    db = get_db()
    try:
        items = db.query("MATCH (i:Item) RETURN i")
        return render_template('items.html', items=items)
    except Exception as e:
        flash(f"Error fetching items: {str(e)}", "danger")
        return redirect(url_for('main.home'))
    finally:
        db.close()

@items_bp.route('/price_override', methods=['POST'])
def price_override():
    item_id = request.form.get('item_id')
    price = request.form.get('price')
    db = get_db()
    try:
        db.query("MATCH (i:Item {uid: $item_id}) SET i.base_price = $price RETURN i", item_id=item_id, price=float(price))
        flash("Price override successful", "success")
    except Exception as e:
        flash(f"Error overriding price: {str(e)}", "danger")
    finally:
        db.close()
    return redirect(url_for('items.items'))

@items_bp.route('/blacklist_item', methods=['POST'])
def blacklist_item():
    item_id = request.form.get('item_id')
    duration = request.form.get('duration')
    db = get_db()
    try:
        db.query("MATCH (i:Item {uid: $item_id}) SET i.blacklisted = true, i.blacklist_duration = $duration RETURN i", item_id=item_id, duration=int(duration))
        flash("Item blacklisted", "success")
    except Exception as e:
        flash(f"Error blacklisting item: {str(e)}", "danger")
    finally:
        db.close()
    return redirect(url_for('items.items'))

@items_bp.route('/lock_item', methods=['POST'])
def lock_item():
    item_id = request.form.get('item_id')
    duration = request.form.get('duration')
    db = get_db()
    try:
        db.query("MATCH (i:Item {uid: $item_id}) SET i.locked = true, i.lock_duration = $duration RETURN i", item_id=item_id, duration=int(duration))
        flash("Item locked", "success")
    except Exception as e:
        flash(f"Error locking item: {str(e)}", "danger")
    finally:
        db.close()
    return redirect(url_for('items.items'))
