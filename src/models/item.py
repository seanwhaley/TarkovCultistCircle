"""Item models for Tarkov data."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class Vendor(BaseModel):
    """Vendor model for trader information."""
    name: str
    normalized_name: Optional[str] = None

class PriceEntry(BaseModel):
    """Price entry model for buy/sell prices."""
    price_rub: int = Field(..., alias="priceRUB")
    vendor: Vendor
    source: Optional[str] = None
    currency: Optional[str] = None

class Category(BaseModel):
    """Category model for item classification."""
    name: str
    id: Optional[str] = None

class ItemProperties(BaseModel):
    """Physical and gameplay properties of items."""
    width: Optional[int] = None
    height: Optional[int] = None
    weight: Optional[float] = None

class ItemBase(BaseModel):
    """Base item model."""
    name: str
    base_price: float = Field(gt=0)
    current_price: Optional[float] = None
    blacklisted: bool = False
    locked: bool = False

class ItemCreate(ItemBase):
    """Item creation model."""
    pass

class ItemUpdate(BaseModel):
    """Item update model."""
    name: Optional[str] = None
    base_price: Optional[float] = Field(default=None, gt=0)
    current_price: Optional[float] = None
    blacklisted: Optional[bool] = None
    locked: Optional[bool] = None

class Item(ItemBase):
    """Complete item model."""
    uid: str
    created_at: datetime
    updated_at: datetime
    price_history: list[dict] = []

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "uid": "123e4567-e89b-12d3-a456-426614174000",
                "name": "GPU",
                "base_price": 100000,
                "current_price": 150000,
                "blacklisted": False,
                "locked": False,
                "created_at": "2024-02-17T00:00:00",
                "updated_at": "2024-02-17T00:00:00",
                "price_history": [
                    {
                        "price": 100000,
                        "timestamp": "2024-02-17T00:00:00"
                    }
                ]
            }
        }
