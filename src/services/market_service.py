"""Market service for price tracking and analysis."""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import statistics

from src.database.neo4j import db
from src.models.item import Item, MarketData, PriceEntry
from src.models.models import Item as ItemNode, PriceHistory, Trade
from src.services.base import BaseService
from src.database.exceptions import DatabaseError
from src.types.responses import PriceHistoryEntry

logger = logging.getLogger(__name__)

class MarketService(BaseService):
    """Service for market analysis and price tracking."""

    def __init__(self):
        self.db = db
        self._price_cache = {}
        self._last_update = None
        self._cache_duration = timedelta(minutes=5)

    async def get_price_history(
        self,
        item_id: str,
        days: int = 7,
        vendor: Optional[str] = None
    ) -> List[PriceHistoryEntry]:
        """Get price history for an item."""
        query = """
        MATCH (i:Item {uid: $item_id})-[:HAD_PRICE]->(ph:PriceHistory)
        WHERE datetime(ph.recorded_at) > datetime() - duration({days: $days})
        AND ($vendor IS NULL OR ph.vendor_name = $vendor)
        RETURN ph.price_rub as price,
               ph.recorded_at as timestamp,
               ph.vendor_name as vendor,
               ph.currency,
               ph.requires_quest
        ORDER BY ph.recorded_at
        """
        return await self._execute_query(
            query,
            {"item_id": item_id, "days": days, "vendor": vendor}
        )

    async def analyze_market_trends(
        self,
        item_id: str,
        timeframe_hours: int = 24
    ) -> MarketData:
        """Analyze market trends for an item."""
        query = """
        MATCH (i:Item {uid: $item_id})-[:HAD_PRICE]->(ph:PriceHistory)
        WHERE datetime(ph.recorded_at) > datetime() - duration({hours: $hours})
        RETURN collect(ph.price_rub) as prices,
               collect(ph.recorded_at) as timestamps
        """
        result = await self._execute_query(
            query,
            {"item_id": item_id, "hours": timeframe_hours},
            single_result=True
        )
        
        if not result or not result['prices']:
            return MarketData()

        prices = result['prices']
        
        # Calculate basic statistics
        current = prices[-1]
        previous = prices[0] if len(prices) > 1 else current
        
        return MarketData(
            change_24h=((current - previous) / previous * 100) if previous else 0,
            change_48h=((current - prices[0]) / prices[0] * 100) if len(prices) > 1 else 0,
            low_24h=min(prices),
            high_24h=max(prices),
            volume_24h=len(prices),
            volatility_score=statistics.stdev(prices) / statistics.mean(prices) if len(prices) > 1 else 0
        )

    async def find_arbitrage_opportunities(
        self,
        min_profit: float = 10000,
        min_profit_percent: float = 10
    ) -> List[Dict[str, Any]]:
        """Find profitable trading opportunities."""
        query = """
        MATCH (i:Item)
        MATCH (i)-[:CAN_BUY_FROM]->(bt:Trade)-[:FROM_VENDOR]->(bv:Vendor)
        MATCH (i)-[:CAN_SELL_TO]->(st:Trade)-[:TO_VENDOR]->(sv:Vendor)
        WHERE bt.priceRUB < st.priceRUB
        AND st.priceRUB - bt.priceRUB >= $min_profit
        AND (st.priceRUB - bt.priceRUB) / bt.priceRUB * 100 >= $min_profit_percent
        RETURN i.name as item_name,
               i.uid as item_id,
               bv.name as buy_vendor,
               sv.name as sell_vendor,
               bt.priceRUB as buy_price,
               st.priceRUB as sell_price,
               st.priceRUB - bt.priceRUB as profit,
               ((st.priceRUB - bt.priceRUB) / bt.priceRUB * 100) as profit_percent
        ORDER BY profit DESC
        """
        return await self._execute_query(
            query,
            {"min_profit": min_profit, "min_profit_percent": min_profit_percent}
        )

    async def track_price_changes(
        self,
        threshold_percent: float = 5
    ) -> List[Dict[str, Any]]:
        """Track significant price changes."""
        query = """
        MATCH (i:Item)-[:HAD_PRICE]->(ph:PriceHistory)
        WITH i, ph
        ORDER BY ph.recorded_at DESC
        WITH i, collect(ph)[0] as latest, collect(ph)[1] as previous
        WHERE abs((latest.price_rub - previous.price_rub) / previous.price_rub * 100) >= $threshold
        RETURN i.name as item_name,
               i.uid as item_id,
               previous.price_rub as old_price,
               latest.price_rub as new_price,
               latest.recorded_at as changed_at,
               ((latest.price_rub - previous.price_rub) / previous.price_rub * 100) as change_percent
        ORDER BY abs(change_percent) DESC
        """
        return await self._execute_query(query, {"threshold": threshold_percent})

    async def update_market_prices(self, prices: List[PriceEntry]) -> None:
        """Bulk update market prices."""
        try:
            for price in prices:
                # Create trade record
                trade_data = {
                    "price_rub": price.price_rub,
                    "vendor_name": price.vendor.name,
                    "currency": price.currency,
                    "requires_quest": price.requires_quest,
                    "recorded_at": datetime.utcnow()
                }
                
                # Update price history
                query = """
                MATCH (i:Item {name: $item_name})
                CREATE (ph:PriceHistory $price_data)
                CREATE (i)-[:HAD_PRICE]->(ph)
                WITH i, ph
                SET i.last_low_price = $price_rub
                """
                await self._execute_query(
                    query,
                    {"item_name": price.item_name, **trade_data}
                )

            self._last_update = datetime.utcnow()
            self._price_cache.clear()
            
        except Exception as e:
            logger.error(f"Failed to update market prices: {str(e)}")
            raise DatabaseError(f"Market price update failed: {str(e)}")

    async def get_market_statistics(self) -> Dict[str, Any]:
        """Get overall market statistics."""
        query = """
        MATCH (i:Item)
        WHERE exists(i.last_low_price) AND exists(i.base_price)
        WITH count(i) as total_items,
             avg(i.last_low_price) as avg_price,
             sum(
                CASE WHEN i.last_low_price > i.base_price
                THEN 1 ELSE 0 END
             ) as items_above_base
        RETURN total_items,
               avg_price,
               items_above_base,
               (items_above_base * 100.0 / total_items) as percent_above_base
        """
        return await self._execute_query(query, single_result=True)
