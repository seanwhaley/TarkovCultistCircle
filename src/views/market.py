"""Market analysis views for item optimization."""
from typing import Dict, Any
from datetime import datetime, timedelta

from flask import render_template, jsonify, request
from flask.views import MethodView

from src.services.market_service import MarketService
from src.services.item_service import ItemService
from src.types.responses import MarketStatistics, TradeOpportunity

market_service = MarketService()
item_service = ItemService()

class MarketOverviewView(MethodView):
    """Market overview and analysis view."""

    async def get(self):
        """Render market overview page."""
        return render_template('market/overview.html')

    async def post(self):
        """Get market analysis data."""
        try:
            stats = await market_service.get_market_statistics()
            changes = await market_service.track_price_changes()
            opportunities = await market_service.find_arbitrage_opportunities()

            return jsonify({
                'success': True,
                'statistics': stats,
                'price_changes': changes,
                'opportunities': opportunities
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

class PriceHistoryView(MethodView):
    """Item price history view."""

    async def get(self, item_id: str):
        """Get item price history."""
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
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

class CraftAnalysisView(MethodView):
    """Crafting analysis view."""

    async def get(self):
        """Render craft analysis page."""
        return render_template('market/crafting.html')

    async def post(self):
        """Get craft analysis data."""
        try:
            min_profit = request.json.get('min_profit', 10000)
            include_barter = request.json.get('include_barter', True)
            
            query = await item_service._execute_query("""
                MATCH (i:Item)<-[:PRODUCES]-(c:Trade {type: 'craft'})
                MATCH (c)-[r:REQUIRES]->(req:Item)
                WITH i, c, collect({
                    item: req,
                    count: toInteger(r.count)
                }) as requirements
                MATCH (i)-[:CAN_SELL_TO]->(st:Trade)
                WHERE st.priceRUB = max(st.priceRUB)
                WITH i, c, requirements, st.priceRUB as sell_price
                WHERE sell_price - reduce(
                    cost = 0,
                    r IN requirements |
                    cost + r.item.last_low_price * r.count
                ) >= $min_profit
                RETURN i.name as item_name,
                       i.uid as item_id,
                       c.station as station,
                       c.level as level,
                       requirements,
                       sell_price,
                       sell_price - reduce(
                           cost = 0,
                           r IN requirements |
                           cost + r.item.last_low_price * r.count
                       ) as profit,
                       c.duration as duration
                ORDER BY profit DESC
            """, {"min_profit": min_profit})

            if include_barter:
                for item in query:
                    barter_trades = await item_service.get_barter_trades(item['item_id'])
                    if barter_trades:
                        item['barter_options'] = barter_trades

            return jsonify({
                'success': True,
                'crafts': query
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

class MarketTrendsView(MethodView):
    """Market trends analysis view."""

    async def get(self):
        """Render market trends page."""
        return render_template('market/trends.html')

    async def post(self):
        """Get market trends data."""
        try:
            timeframe = request.json.get('timeframe', 24)
            threshold = request.json.get('threshold', 5)
            
            # Get significant price changes
            changes = await market_service.track_price_changes(
                threshold_percent=threshold
            )
            
            # Get market statistics
            stats = await market_service.get_market_statistics()
            
            # Analyze specific items if provided
            items = request.json.get('items', [])
            item_trends = {}
            if items:
                for item_id in items:
                    trends = await market_service.analyze_market_trends(
                        item_id,
                        timeframe_hours=timeframe
                    )
                    item_trends[item_id] = trends.model_dump()

            return jsonify({
                'success': True,
                'changes': changes,
                'statistics': stats,
                'item_trends': item_trends
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

# Register views
market_overview = MarketOverviewView.as_view('market_overview')
price_history = PriceHistoryView.as_view('price_history')
craft_analysis = CraftAnalysisView.as_view('craft_analysis')
market_trends = MarketTrendsView.as_view('market_trends')