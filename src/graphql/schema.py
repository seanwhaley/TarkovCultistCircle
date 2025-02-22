from datetime import datetime
from typing import List, Optional

import strawberry
from strawberry.types import Info
from strawberry.fastapi import GraphQLRouter

from src.core.deps import get_current_user, get_item_service
from src.models.item import Item
from src.models.user import User

@strawberry.type
class ItemType:
    uid: str
    name: str
    base_price: float
    current_price: Optional[float]
    blacklisted: bool
    locked: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_pydantic(cls, item: Item) -> "ItemType":
        return cls(
            uid=item.uid,
            name=item.name,
            base_price=item.base_price,
            current_price=item.current_price,
            blacklisted=item.blacklisted,
            locked=item.locked,
            created_at=item.created_at,
            updated_at=item.updated_at
        )

@strawberry.type
class MarketAnalytics:
    volatility: float
    trend: str
    confidence: float
    volume: int
    price_change_24h: float

@strawberry.type
class Query:
    @strawberry.field
    async def items(
        self,
        info: Info,
        skip: int = 0,
        limit: int = 100
    ) -> List[ItemType]:
        service = await get_item_service(info.context["request"])
        items = await service.get_items(skip=skip, limit=limit)
        return [ItemType.from_pydantic(item) for item in items]

    @strawberry.field
    async def item(
        self,
        info: Info,
        item_id: str
    ) -> Optional[ItemType]:
        service = await get_item_service(info.context["request"])
        try:
            item = await service.get_by_id(item_id)
            return ItemType.from_pydantic(item)
        except:
            return None

    @strawberry.field
    async def market_analytics(
        self,
        info: Info,
        item_id: str
    ) -> Optional[MarketAnalytics]:
        service = await get_item_service(info.context["request"])
        try:
            analytics = await service.get_market_analytics(item_id)
            return MarketAnalytics(**analytics)
        except:
            return None

@strawberry.type
class ItemInput:
    name: str
    base_price: float
    current_price: Optional[float] = None
    blacklisted: bool = False
    locked: bool = False

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_item(
        self,
        info: Info,
        input: ItemInput
    ) -> ItemType:
        current_user = await get_current_user(info.context["request"])
        if not current_user.is_admin:
            raise PermissionError("Admin access required")
            
        service = await get_item_service(info.context["request"])
        item = await service.create(input.__dict__)
        return ItemType.from_pydantic(item)

    @strawberry.mutation
    async def override_price(
        self,
        info: Info,
        item_id: str,
        price: float
    ) -> ItemType:
        service = await get_item_service(info.context["request"])
        item = await service.override_price(item_id, price)
        return ItemType.from_pydantic(item)

    @strawberry.mutation
    async def blacklist_item(
        self,
        info: Info,
        item_id: str
    ) -> ItemType:
        service = await get_item_service(info.context["request"])
        item = await service.blacklist_item(item_id)
        return ItemType.from_pydantic(item)

    @strawberry.mutation
    async def lock_item(
        self,
        info: Info,
        item_id: str
    ) -> ItemType:
        service = await get_item_service(info.context["request"])
        item = await service.lock_item(item_id)
        return ItemType.from_pydantic(item)

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)
