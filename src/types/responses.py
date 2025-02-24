"""Type definitions for API responses."""
from typing import Dict, Any, List, Optional, TypeVar, Generic, Union
from datetime import datetime
from pydantic import BaseModel, Field

T = TypeVar('T')
JsonDict = Dict[str, Any]

class ErrorInfo(BaseModel):
    """Error information model."""
    message: str
    code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class PaginationInfo(BaseModel):
    """Pagination information."""
    page: int = 1
    per_page: int = 20
    total: int
    pages: int

class PriceHistoryEntry(BaseModel):
    """Price history entry for items."""
    price: float
    timestamp: datetime
    vendor: str
    currency: Optional[str] = None
    requires_quest: Optional[bool] = None

class MarketAnalysis(BaseModel):
    """Market analysis data."""
    volatility: float
    trend: str  # "up", "down", "stable"
    confidence: float  # 0-1 scale
    volume: int
    price_change_24h: float

class CraftRequirement(BaseModel):
    """Craft requirement information."""
    item_name: str
    quantity: int
    base_price: float
    current_price: Optional[float] = None

class CraftAnalysis(BaseModel):
    """Craft profitability analysis."""
    station: str
    level: int
    duration: int
    requirements: List[CraftRequirement]
    output_count: int = 1
    total_cost: float
    sell_price: float
    profit: float
    profit_per_hour: float

class TradeOpportunity(BaseModel):
    """Trading opportunity information."""
    item_name: str
    buy_price: float
    sell_price: float
    profit: float
    profit_percent: float
    buy_vendor: str
    sell_vendor: str
    market_data: Optional[Dict[str, Any]] = None
    barter_options: Optional[List[Dict[str, Any]]] = None
    craft_options: Optional[List[Dict[str, Any]]] = None

class MarketStatistics(BaseModel):
    """Overall market statistics."""
    total_items: int
    avg_price: float
    items_above_base: int
    percent_above_base: float
    volatility_index: Optional[float] = None
    trade_volume_24h: Optional[int] = None

class ItemResponse(BaseModel):
    """Standard item response."""
    uid: str
    name: str
    base_price: float
    current_price: Optional[float] = None
    market_analysis: Optional[MarketAnalysis] = None
    price_history: Optional[List[PriceHistoryEntry]] = None
    craft_analysis: Optional[CraftAnalysis] = None

class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    data: List[T]
    pagination: PaginationInfo

class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    success: bool
    data: Optional[T] = None
    error: Optional[ErrorInfo] = None
    metadata: Optional[Dict[str, Any]] = None

ResponseType = Union[
    ItemResponse,
    List[ItemResponse],
    PaginatedResponse[ItemResponse],
    MarketStatistics,
    List[TradeOpportunity],
    List[PriceHistoryEntry]
]
