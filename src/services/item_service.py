"""Item service layer handling item-related operations."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import logging

from src.core.cache import cache, invalidate_cache
from src.core.exceptions import ValidationError, NotFoundError
from src.models.item import Item, ItemCreate, ItemUpdate
from src.services.base import BaseService

logger = logging.getLogger(__name__)

class ItemService(BaseService[Item]):
    """Service for handling item operations."""
    
    def __init__(self, db_session):
        super().__init__(db_session)
        self.model_class = Item

    @cache(expire=300)  # Cache for 5 minutes
    async def get_items(
        self,
        skip: int = 0,
        limit: int = 100,
        include_blacklisted: bool = False
    ) -> List[Item]:
        """Get items with optional filtering."""
        query = """
        MATCH (i:Item)
        WHERE i.blacklisted = false OR $include_blacklisted = true
        RETURN i
        ORDER BY i.name
        SKIP $skip
        LIMIT $limit
        """
        result = await self._execute_query(
            query,
            {"skip": skip, "limit": limit, "include_blacklisted": include_blacklisted}
        )
        return [Item(**item["i"]) for item in result]

    async def override_price(self, item_id: str, price: float) -> Item:
        """Override an item's price."""
        if price <= 0:
            raise ValidationError("Price must be greater than 0")

        query = """
        MATCH (i:Item {uid: $item_id})
        WHERE NOT i.locked
        SET i.current_price = $price,
            i.updated_at = $timestamp,
            i.price_history = i.price_history + [{
                price: $price,
                timestamp: $timestamp,
                type: 'override'
            }]
        RETURN i
        """
        result = await self._execute_query(
            query,
            {
                "item_id": item_id,
                "price": price,
                "timestamp": datetime.utcnow().isoformat()
            },
            single_result=True
        )
        if not result:
            raise NotFoundError("Item not found or is locked")
        
        # Invalidate cache for this item
        await invalidate_cache(f"items:{item_id}")
        return Item(**result["i"])

    async def blacklist_item(self, item_id: str) -> Item:
        """Blacklist an item."""
        query = """
        MATCH (i:Item {uid: $item_id})
        SET i.blacklisted = true,
            i.updated_at = $timestamp
        RETURN i
        """
        result = await self._execute_query(
            query,
            {
                "item_id": item_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            single_result=True
        )
        if not result:
            raise NotFoundError("Item not found")
        
        # Invalidate cache for items list
        await invalidate_cache("items:*")
        return Item(**result["i"])

    async def lock_item(self, item_id: str) -> Item:
        """Lock an item's price."""
        query = """
        MATCH (i:Item {uid: $item_id})
        SET i.locked = true,
            i.updated_at = $timestamp
        RETURN i
        """
        result = await self._execute_query(
            query,
            {
                "item_id": item_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            single_result=True
        )
        if not result:
            raise NotFoundError("Item not found")
        
        # Invalidate cache for this item
        await invalidate_cache(f"items:{item_id}")
        return Item(**result["i"])

    @cache(expire=300)
    async def get_market_analytics(self, item_id: str) -> Dict[str, Any]:
        """Get market analytics for an item."""
        query = """
        MATCH (i:Item {uid: $item_id})
        WITH i, i.price_history as history
        WHERE size(history) > 0
        WITH i,
             history[size(history)-1].price as current_price,
             history[size(history)-2].price as previous_price,
             [price in history | price.price] as prices
        RETURN {
            volatility: reduce(v = 0.0, p in prices |
                v + pow(p - avg(prices), 2)) / size(prices),
            trend: CASE
                WHEN current_price > previous_price THEN 'up'
                WHEN current_price < previous_price THEN 'down'
                ELSE 'stable'
            END,
            confidence: CASE
                WHEN size(prices) < 10 THEN 0.5
                ELSE 0.8
            END,
            volume: size(history),
            price_change_24h: ((current_price - previous_price) / previous_price) * 100
        } as analytics
        """
        result = await self._execute_query(query, {"item_id": item_id}, single_result=True)
        if not result:
            raise NotFoundError("Item not found or has no price history")
        return result["analytics"]

    async def optimize_purchases(
        self,
        item_ids: List[str],
        budget: float,
        max_items: Optional[int] = None,
        min_profit: Optional[float] = None
    ) -> Dict[str, Any]:
        """Calculate optimal item purchases within budget."""
        query = """
        MATCH (i:Item)
        WHERE i.uid IN $item_ids
            AND NOT i.blacklisted
            AND i.current_price > 0
        WITH i
        ORDER BY (i.base_price - i.current_price) / i.current_price DESC
        WITH collect({
            item: i,
            profit_margin: (i.base_price - i.current_price) / i.current_price
        }) as items
        WITH [item in items WHERE 
            item.profit_margin >= $min_profit_margin] as filtered_items
        RETURN {
            items: [item in filtered_items[..$max_items] |
                {
                    uid: item.item.uid,
                    name: item.item.name,
                    current_price: item.item.current_price,
                    potential_profit: item.item.base_price - item.item.current_price,
                    profit_margin: item.profit_margin
                }
            ],
            total_cost: reduce(cost = 0.0, item in filtered_items[..$max_items] |
                cost + item.item.current_price),
            expected_profit: reduce(profit = 0.0, item in filtered_items[..$max_items] |
                profit + (item.item.base_price - item.item.current_price)),
            profit_margin: reduce(margin = 0.0, item in filtered_items[..$max_items] |
                margin + item.profit_margin) / size(filtered_items[..$max_items])
        } as result
        """
        result = await self._execute_query(
            query,
            {
                "item_ids": item_ids,
                "max_items": max_items or len(item_ids),
                "min_profit_margin": min_profit / 100 if min_profit else 0
            },
            single_result=True
        )
        if not result or not result["result"]["items"]:
            raise ValidationError("No valid items found for optimization")
        
        # Validate budget constraints
        if result["result"]["total_cost"] > budget:
            raise ValidationError("Total cost exceeds budget")
            
        return result["result"]

    @cache(expire=60)
    async def get_investment_suggestions(
        self,
        budget: float,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get investment suggestions based on budget."""
        query = """
        MATCH (i:Item)
        WHERE NOT i.blacklisted
            AND i.current_price <= $budget
            AND i.current_price > 0
        WITH i,
            (i.base_price - i.current_price) / i.current_price as profit_margin
        ORDER BY profit_margin DESC
        LIMIT $limit
        RETURN collect({
            uid: i.uid,
            name: i.name,
            current_price: i.current_price,
            potential_profit: i.base_price - i.current_price,
            profit_margin: profit_margin
        }) as suggestions
        """
        result = await self._execute_query(
            query,
            {"budget": budget, "limit": limit},
            single_result=True
        )
        return result["suggestions"] if result else []
