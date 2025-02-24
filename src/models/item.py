"""Item models for Tarkov data."""
from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class Vendor(BaseModel):
    """Vendor model for trader information."""
    name: str
    normalized_name: Optional[str] = None
    min_level: Optional[int] = None
    enabled: bool = True

class PriceEntry(BaseModel):
    """Price entry model for buy/sell prices."""
    price_rub: int = Field(..., alias="priceRUB")
    vendor: Vendor
    source: Optional[str] = None
    currency: Optional[str] = None
    requires_quest: Optional[bool] = None
    restock_amount: Optional[int] = None

class Material(BaseModel):
    """Material properties for armor."""
    name: str
    destructibility: float

class ArmorProperties(BaseModel):
    """Armor specific properties."""
    class_level: int = Field(..., alias="class")
    zones: List[str]
    durability: int
    material: Material

class WeaponStats(BaseModel):
    """Weapon specific properties."""
    caliber: str
    firerate: int
    ergonomics: int
    recoil_vertical: int = Field(..., alias="recoilVertical")
    recoil_horizontal: int = Field(..., alias="recoilHorizontal")

class ItemProperties(BaseModel):
    """Physical and gameplay properties of items."""
    width: Optional[int] = None
    height: Optional[int] = None
    weight: Optional[float] = None
    armor: Optional[ArmorProperties] = None
    weapon_stats: Optional[WeaponStats] = None
    grid_image_link: Optional[str] = None
    wiki_link: Optional[str] = None
    has_grid: Optional[bool] = None
    blocks_headphones: Optional[bool] = None
    max_stackable: Optional[int] = None

class MarketData(BaseModel):
    """Market-related data for items."""
    change_24h: Optional[float] = None
    change_48h: Optional[float] = None
    low_24h: Optional[int] = None
    high_24h: Optional[int] = None
    volume_24h: Optional[int] = None
    trades_24h: Optional[int] = None
    volatility_score: Optional[float] = None

class ItemBase(BaseModel):
    """Base item model."""
    name: str
    base_price: float = Field(gt=0)
    current_price: Optional[float] = None
    blacklisted: bool = False
    locked: bool = False
    properties: Optional[ItemProperties] = None
    market_data: Optional[MarketData] = None

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
    properties: Optional[ItemProperties] = None
    market_data: Optional[MarketData] = None

class Item(ItemBase):
    """Complete item model."""
    uid: str
    created_at: datetime
    updated_at: datetime
    price_history: List[PriceEntry] = []
    buy_from: List[PriceEntry] = []
    sell_to: List[PriceEntry] = []

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "uid": "123e4567-e89b-12d3-a456-426614174000",
                "name": "SVDS",
                "base_price": 100000,
                "current_price": 150000,
                "blacklisted": False,
                "locked": False,
                "properties": {
                    "width": 2,
                    "height": 1,
                    "weight": 4.3,
                    "weapon_stats": {
                        "caliber": "7.62x54R",
                        "firerate": 700,
                        "ergonomics": 45,
                        "recoil_vertical": 145,
                        "recoil_horizontal": 400
                    }
                },
                "market_data": {
                    "change_24h": -5.2,
                    "volume_24h": 1200,
                    "volatility_score": 0.75
                },
                "created_at": "2024-02-17T00:00:00",
                "updated_at": "2024-02-17T00:00:00",
                "price_history": []
            }
        }
