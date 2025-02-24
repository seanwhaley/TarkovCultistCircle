"""Price history model."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class PriceHistoryBase(BaseModel):
    """Base model for price history entries."""
    timestamp: datetime = Field(..., description="When the price was recorded")
    price: float = Field(..., ge=0, description="Item price in roubles")
    type: str = Field("market", description="Type of price (market, vendor, etc)")

class PriceHistory(PriceHistoryBase):
    """Price history model with database ID."""
    id: str = Field(..., description="Unique identifier")
    item_id: str = Field(..., description="Associated item ID")
    recorded_by: Optional[str] = Field(None, description="User who recorded the price")

class PriceHistoryCreate(PriceHistoryBase):
    """Model for creating new price history entries."""
    item_id: str = Field(..., description="Associated item ID")

class PriceHistoryInDB(PriceHistory):
    """Internal database model for price history."""
    class Config:
        from_attributes = True