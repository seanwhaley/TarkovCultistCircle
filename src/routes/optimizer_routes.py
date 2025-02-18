from flask import Blueprint, render_template, request, jsonify
from src.db import get_db

optimizer_bp = Blueprint('optimizer', __name__)

@optimizer_bp.route('/optimizer')
def optimizer():
    return render_template('optimizer.html')

@optimizer_bp.route('/optimal_combinations')
def optimal_combinations():
    db = get_db()
    query = """
    MATCH (i:Item)
    WHERE NOT (i)-[:IS_BLACKLISTED]->(:BlacklistEntry)
      AND toInteger(i.basePrice) >= 400000
    RETURN i
    ORDER BY toInteger(i.basePrice) DESC
    LIMIT 5
    """
    items = db.query(query)
    db.close()
    return render_template('optimal_combinations.html', items=items)

@optimizer_bp.route('/api/optimize', methods=["POST"])
def optimize():
    try:
        data = request.get_json()
        min_price = int(data.get("minPrice", 400000))
        max_items = min(int(data.get("maxItems", 5)), 5)
        
        db = get_db()
        query = """
        MATCH (i:Item)
        WHERE NOT (i)-[:IS_BLACKLISTED]->(:BlacklistEntry)
        WITH i, toInteger(i.basePrice) as price
        WHERE price > 0
        RETURN i.id as id, i.name as name, price as basePrice, i.lastLowPrice as lastLowPrice,
               i.avg24hPrice as avg24hPrice, i.updated as updated
        ORDER BY price DESC
        """
        
        items = db.query(query)
        
        # Convert string prices to integers for comparison
        for item in items:
            item['basePrice'] = int(item['basePrice'])
            item['lastLowPrice'] = int(item['lastLowPrice']) if item['lastLowPrice'] else 0
            item['avg24hPrice'] = int(item['avg24hPrice']) if item['avg24hPrice'] else 0
        
        # Find optimal combinations
        def find_combinations(items, min_total, max_count):
            results = []
            def backtrack(start, combo, total):
                if total >= min_total and len(combo) <= max_count:
                    results.append(combo.copy())
                if len(combo) >= max_count:
                    return
                
                for i in range(start, len(items)):
                    combo.append(items[i])
                    backtrack(i + 1, combo, total + items[i]['basePrice'])
                    combo.pop()
            
            backtrack(0, [], 0)
            return results
        
        combinations = find_combinations(items, min_price, max_items)
        
        # Sort combinations by total value
        combinations.sort(key=lambda x: sum(item['basePrice'] for item in x), reverse=True)
        
        # Format response
        result = [{
            'totalValue': sum(item['basePrice'] for item in combo),
            'items': combo
        } for combo in combinations[:10]]  # Return top 10 combinations
        
        db.close()
        return jsonify({"success": True, "combinations": result})
        
    except ValueError as e:
        return jsonify({"success": False, "error": "Invalid numeric value provided"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
