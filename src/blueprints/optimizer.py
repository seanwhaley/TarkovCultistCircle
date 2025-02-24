"""Blueprint for item optimization features."""
import logging
from typing import Dict, Any, List

from flask import Blueprint, current_app, jsonify, render_template, request
from flask_login import login_required

from src.core.neo4j import Neo4jClient
from src.services.item_service import ItemService
from src.services.market_service import MarketService
from src.services.exceptions import OptimizationError
from src.models.item import Item
from src.blueprints.auth import admin_required

optimizer_bp = Blueprint('optimizer', __name__)
item_service = ItemService()
market_service = MarketService()
logger = logging.getLogger(__name__)

@optimizer_bp.route('/')
def index():
    """Main optimization interface"""
    return render_template('optimizer/index.html')

@optimizer_bp.route('/optimize', methods=['POST'])
async def optimize():
    """Find optimal item combinations"""
    try:
        data = request.get_json()
        budget = data.get('budget', 0)
        trader_levels = data.get('trader_levels', {})
        include_barter = data.get('include_barter', True)
        include_craft = data.get('include_craft', True)

        # Get arbitrage opportunities
        opportunities = await market_service.find_arbitrage_opportunities(
            min_profit=10000,  # Configurable minimum profit
            min_profit_percent=10  # Configurable minimum profit percentage
        )

        # Filter by trader levels and budget
        filtered_opportunities = [
            opp for opp in opportunities
            if opp['buy_price'] <= budget and
            all(level >= trader_levels.get(vendor, 0) 
                for vendor, level in trader_levels.items())
        ]

        # Include barter trades if requested
        if include_barter:
            for opp in filtered_opportunities:
                barter_trades = await item_service.get_barter_trades(opp['item_id'])
                if barter_trades:
                    opp['barter_options'] = barter_trades

        # Include crafting if requested
        if include_craft:
            for opp in filtered_opportunities:
                craft_reqs = await item_service.get_craft_requirements(opp['item_id'])
                if craft_reqs:
                    opp['craft_options'] = craft_reqs

        # Calculate market trends
        for opp in filtered_opportunities:
            market_data = await market_service.analyze_market_trends(opp['item_id'])
            opp['market_trends'] = market_data.model_dump()

        return jsonify({
            'success': True,
            'opportunities': filtered_opportunities
        })

    except Exception as e:
        logger.error(f"Optimization error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@optimizer_bp.route('/price-override', methods=['POST'])
@admin_required
async def set_price_override():
    """Override item price (admin only)"""
    try:
        data = request.get_json()
        item_id = data['item_id']
        new_price = data['price']
        
        # Create price override
        await item_service.create_price_override(item_id, new_price)
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Price override error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@optimizer_bp.route('/market-analysis', methods=['GET'])
async def market_analysis():
    """Get market analysis data"""
    try:
        # Get overall market statistics
        stats = await market_service.get_market_statistics()
        
        # Get significant price changes
        changes = await market_service.track_price_changes(threshold_percent=5)
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'significant_changes': changes
        })
    except Exception as e:
        logger.error(f"Market analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@optimizer_bp.route('/item/<item_id>/history', methods=['GET'])
async def price_history(item_id: str):
    """Get item price history"""
    try:
        days = request.args.get('days', 7, type=int)
        vendor = request.args.get('vendor')
        
        history = await market_service.get_price_history(
            item_id,
            days=days,
            vendor=vendor
        )
        
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        logger.error(f"Price history error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@optimizer_bp.route('/blacklist', methods=['POST'])
@admin_required
async def manage_blacklist():
    """Manage item blacklist"""
    try:
        data = request.get_json()
        item_id = data['item_id']
        action = data['action']  # 'add' or 'remove'
        
        if action == 'add':
            await item_service.blacklist_item(item_id)
        else:
            await item_service.remove_from_blacklist(item_id)
            
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Blacklist management error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@optimizer_bp.route('/craft-analysis', methods=['GET'])
async def analyze_crafts():
    """Analyze craft profitability"""
    try:
        # Get all items with crafts
        query = """
        MATCH (i:Item)<-[:PRODUCES]-(c:Trade {type: 'craft'})
        MATCH (c)-[r:REQUIRES]->(req:Item)
        WITH i, c, collect({item: req, count: toInteger(r.count)}) as requirements
        MATCH (i)-[:CAN_SELL_TO]->(st:Trade)
        WHERE st.priceRUB = max(st.priceRUB)
        WITH i, c, requirements, st.priceRUB as sell_price
        RETURN i.name as item_name,
               i.uid as item_id,
               c.station as station,
               requirements,
               sell_price,
               sell_price - reduce(
                   cost = 0,
                   r IN requirements |
                   cost + r.item.last_low_price * r.count
               ) as profit
        ORDER BY profit DESC
        """
        
        crafts = await item_service._execute_query(query)
        
        return jsonify({
            'success': True,
            'craft_analysis': crafts
        })
    except Exception as e:
        logger.error(f"Craft analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
