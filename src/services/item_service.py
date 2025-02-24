"""Item service with relationship and market data handling."""
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from src.database.neo4j import db
from src.models.item import Item, ItemCreate, ItemUpdate, PriceEntry
from src.models.models import (
    Item as ItemNode, PriceHistory, Trade, 
    Armor, Material, WeaponStats
)
from src.services.base import BaseService
from src.database.exceptions import DatabaseError

logger = logging.getLogger(__name__)

class ItemService(BaseService):
    """Service for managing items and their relationships."""

    def __init__(self):
        self.db = db
        self.model_class = ItemNode

    async def create_item(self, item: ItemCreate) -> Item:
        """Create a new item with all its relationships."""
        try:
            # Create base item node
            item_data = item.model_dump()
            item_node = ItemNode(**item_data).save()

            # Handle armor properties if present
            if item.properties and item.properties.armor:
                armor_data = item.properties.armor.model_dump()
                material_data = armor_data.pop('material')
                
                # Create or get material
                material = Material.nodes.get_or_none(name=material_data['name'])
                if not material:
                    material = Material(**material_data).save()
                
                # Create armor with material relationship
                armor = Armor(**armor_data).save()
                armor.material.connect(material)
                item_node.armor.connect(armor)

            # Handle weapon stats if present
            if item.properties and item.properties.weapon_stats:
                stats_data = item.properties.weapon_stats.model_dump()
                stats = WeaponStats(**stats_data).save()
                item_node.weapon_stats.connect(stats)

            return Item.model_validate(item_node.__properties__)
        except Exception as e:
            logger.error(f"Failed to create item: {str(e)}")
            raise DatabaseError(f"Item creation failed: {str(e)}")

    async def update_market_data(self, item_id: str, price_entry: PriceEntry) -> None:
        """Update item's price history and market data."""
        try:
            item = ItemNode.nodes.get(uid=item_id)
            
            # Create price history entry
            history = PriceHistory(
                price_rub=price_entry.price_rub,
                vendor_name=price_entry.vendor.name,
                currency=price_entry.currency,
                requires_quest=price_entry.requires_quest,
                restock_amount=price_entry.restock_amount
            ).save()
            
            # Connect price history to item
            item.price_history.connect(history)
            
            # Update market data
            market_data = item.market_data or {}
            market_data['last_update'] = datetime.utcnow().isoformat()
            market_data['last_price'] = price_entry.price_rub
            
            # Calculate price changes
            prev_prices = [ph.price_rub for ph in item.price_history.all()]
            if prev_prices:
                market_data['change_24h'] = (
                    (price_entry.price_rub - prev_prices[-1]) / prev_prices[-1]
                ) * 100 if prev_prices[-1] else 0
            
            item.market_data = market_data
            item.save()

        except Exception as e:
            logger.error(f"Failed to update market data: {str(e)}")
            raise DatabaseError(f"Market data update failed: {str(e)}")

    async def get_craft_requirements(self, item_id: str) -> List[Dict[str, Any]]:
        """Get crafting requirements for an item."""
        query = """
        MATCH (i:Item {uid: $item_id})<-[:PRODUCES]-(c:Trade {type: 'craft'})
        MATCH (c)-[r:REQUIRES]->(req:Item)
        RETURN req.name as item_name, 
               req.base_price as base_price,
               r.count as quantity,
               c.station as station,
               c.level as level
        """
        return await self._execute_query(query, {"item_id": item_id})

    async def get_barter_trades(self, item_id: str) -> List[Dict[str, Any]]:
        """Get barter trades involving an item."""
        query = """
        MATCH (i:Item {uid: $item_id})<-[:GIVES]-(b:Trade {type: 'barter'})
        MATCH (b)-[r:REQUIRES]->(req:Item)
        MATCH (b)-[:AVAILABLE_AT]->(v:Vendor)
        RETURN v.name as vendor_name,
               collect({
                   name: req.name,
                   quantity: r.count,
                   base_price: req.base_price
               }) as requirements
        """
        return await self._execute_query(query, {"item_id": item_id})

    async def calculate_profit_margin(self, item_id: str) -> Dict[str, float]:
        """Calculate potential profit margins for an item."""
        query = """
        MATCH (i:Item {uid: $item_id})
        MATCH (i)-[:CAN_BUY_FROM]->(bt:Trade)-[:FROM_VENDOR]->(bv:Vendor)
        MATCH (i)-[:CAN_SELL_TO]->(st:Trade)-[:TO_VENDOR]->(sv:Vendor)
        WITH i, bt, st, bv, sv,
             bt.priceRUB as buy_price,
             st.priceRUB as sell_price
        WHERE buy_price < sell_price
        RETURN bv.name as buy_vendor,
               sv.name as sell_vendor,
               buy_price,
               sell_price,
               sell_price - buy_price as profit,
               ((sell_price - buy_price) / buy_price * 100) as profit_percent
        ORDER BY profit DESC
        """
        return await self._execute_query(query, {"item_id": item_id})
