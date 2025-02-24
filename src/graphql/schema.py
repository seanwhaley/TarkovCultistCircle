from datetime import datetime
from typing import List, Optional

import strawberry
from strawberry.types import Info

from src.services.item_service import ItemService
from src.services.market_service import MarketService
from src.models.item import Item, MarketData, PriceEntry

item_service = ItemService()
market_service = MarketService()

@strawberry.type
class MarketAnalysisType:
    volatility: float
    trend: str
    confidence: float
    volume: int
    price_change_24h: float

@strawberry.type
class PriceHistoryType:
    price: float
    timestamp: datetime
    vendor: str
    currency: Optional[str]
    requires_quest: Optional[bool]

@strawberry.type
class CraftRequirementType:
    item_name: str
    quantity: int
    base_price: float
    current_price: Optional[float]

@strawberry.type
class CraftAnalysisType:
    station: str
    level: int
    duration: int
    requirements: List[CraftRequirementType]
    output_count: int
    total_cost: float
    sell_price: float
    profit: float
    profit_per_hour: float

@strawberry.type
class TradeOpportunityType:
    item_name: str
    buy_price: float
    sell_price: float
    profit: float
    profit_percent: float
    buy_vendor: str
    sell_vendor: str
    market_data: Optional[MarketAnalysisType]
    barter_options: Optional[List[str]]
    craft_options: Optional[List[CraftRequirementType]]

@strawberry.type
class MarketStatisticsType:
    total_items: int
    avg_price: float
    items_above_base: int
    percent_above_base: float
    volatility_index: Optional[float]
    trade_volume_24h: Optional[int]

@strawberry.type
class ItemType:
    uid: str
    name: str
    base_price: float
    current_price: Optional[float]
    properties: Optional[dict]
    market_data: Optional[MarketAnalysisType]
    price_history: List[PriceHistoryType]
    craft_analysis: Optional[CraftAnalysisType]

@strawberry.type
class Query:
    @strawberry.field
    async def item(self, info: Info, item_id: str) -> Optional[ItemType]:
        """Get a single item by ID."""
        return await item_service.get_by_id(item_id)

    @strawberry.field
    async def items(
        self,
        info: Info,
        search: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: int = 20
    ) -> List[ItemType]:
        """Search for items with filters."""
        return await item_service.search_items(
            search=search,
            category=category,
            min_price=min_price,
            max_price=max_price,
            limit=limit
        )

    @strawberry.field
    async def market_statistics(self, info: Info) -> MarketStatisticsType:
        """Get overall market statistics."""
        return await market_service.get_market_statistics()

    @strawberry.field
    async def price_history(
        self,
        info: Info,
        item_id: str,
        days: int = 7,
        vendor: Optional[str] = None
    ) -> List[PriceHistoryType]:
        """Get price history for an item."""
        return await market_service.get_price_history(
            item_id=item_id,
            days=days,
            vendor=vendor
        )

    @strawberry.field
    async def trade_opportunities(
        self,
        info: Info,
        min_profit: float = 10000,
        min_profit_percent: float = 10
    ) -> List[TradeOpportunityType]:
        """Find profitable trading opportunities."""
        return await market_service.find_arbitrage_opportunities(
            min_profit=min_profit,
            min_profit_percent=min_profit_percent
        )

    @strawberry.field
    async def craft_analysis(
        self,
        info: Info,
        min_profit: Optional[float] = None
    ) -> List[CraftAnalysisType]:
        """Analyze craft profitability."""
        return await item_service.analyze_crafts(min_profit=min_profit)

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def update_price(
        self,
        info: Info,
        item_id: str,
        price: float,
        vendor: str
    ) -> ItemType:
        """Update item price."""
        entry = PriceEntry(
            price_rub=price,
            vendor={"name": vendor}
        )
        await market_service.update_market_prices([entry])
        return await item_service.get_by_id(item_id)

    @strawberry.mutation
    async def blacklist_item(
        self,
        info: Info,
        item_id: str
    ) -> bool:
        """Add item to blacklist."""
        await item_service.blacklist_item(item_id)
        return True

    @strawberry.mutation
    async def remove_from_blacklist(
        self,
        info: Info,
        item_id: str
    ) -> bool:
        """Remove item from blacklist."""
        await item_service.remove_from_blacklist(item_id)
        return True

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)
