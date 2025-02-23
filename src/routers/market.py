from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.core.deps import get_current_user, get_item_service
from src.models.user import User
from src.services.item_service import ItemService

router = APIRouter()

class PriceHistory(BaseModel):
    """Price history model."""
    timestamp: datetime
    price: float

class MarketAnalytics(BaseModel):
    """Market analytics model."""
    volatility: float
    trend: str
    confidence: float
    volume: int
    price_change_24h: float

@router.get("/analytics/{item_id}", response_model=MarketAnalytics)
async def get_market_analytics(
    item_id: str,
    service: ItemService = Depends(get_item_service),
    current_user: User = Depends(get_current_user)
) -> MarketAnalytics:
    """Get market analytics for an item."""
    try:
        analytics = await service.get_market_analytics(item_id)
        return MarketAnalytics(**analytics)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/price-history/{item_id}", response_model=List[PriceHistory])
async def get_price_history(
    item_id: str,
    days: int = Query(7, ge=1, le=30),
    service: ItemService = Depends(get_item_service),
    current_user: User = Depends(get_current_user)
) -> List[PriceHistory]:
    """Get price history for an item."""
    try:
        history = await service.get_price_history(item_id, days)
        return [PriceHistory(**h) for h in history]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/trending", response_model=List[dict])
async def get_trending_items(
    limit: int = Query(10, ge=1, le=100),
    service: ItemService = Depends(get_item_service),
    current_user: User = Depends(get_current_user)
) -> List[dict]:
    """Get trending items in the market."""
    try:
        return await service.get_trending_items(limit)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )