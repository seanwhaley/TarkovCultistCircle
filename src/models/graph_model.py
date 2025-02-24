"""Neo4j graph models and validation."""
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

class NodeLabels(Enum):
    ITEM = "Item"
    VENDOR = "Vendor"
    CATEGORY = "Category"
    PRICE_HISTORY = "PriceHistory"
    BARTER = "Barter"
    CRAFT = "Craft"
    ARMOR = "Armor"
    MATERIAL = "Material"
    WEAPON_STATS = "WeaponStats"
    TRADE = "Trade"

class RelationshipTypes(Enum):
    HAD_PRICE = "HAD_PRICE"
    IN_CATEGORY = "IN_CATEGORY"
    VENDOR_BOUGHT = "VENDOR_BOUGHT"
    VENDOR_SOLD = "VENDOR_SOLD"
    USED_IN_CRAFT = "USED_IN_CRAFT"
    USED_IN_BARTER = "USED_IN_BARTER"
    HAS_ARMOR = "HAS_ARMOR"
    MADE_OF = "MADE_OF"
    HAS_STATS = "HAS_STATS"
    REQUIRES = "REQUIRES"
    WITH_COUNT = "WITH_COUNT"
    PRODUCES = "PRODUCES"
    AT_STATION = "AT_STATION"
    FROM_VENDOR = "FROM_VENDOR"
    TO_VENDOR = "TO_VENDOR"

@dataclass
class NodeProperties:
    class Item:
        required = {
            'id': str,
            'name': str,
            'normalized_name': str,
            'base_price': float,
            'updated': datetime
        }
        optional = {
            'short_name': str,
            'weight': float,
            'width': int,
            'height': int,
            'grid_image_link': str,
            'wiki_link': str,
            'has_grid': bool,
            'blocks_headphones': bool,
            'max_stackable': int,
            'last_low_price': float,
            'avg_24h_price': float
        }

    class PriceHistory:
        required = {
            'price_rub': float,
            'recorded_at': datetime,
            'vendor_name': str
        }
        optional = {
            'currency': str,
            'original_price': float,
            'requires_quest': bool,
            'restock_amount': int
        }

    class Vendor:
        required = {
            'name': str,
            'normalized_name': str
        }
        optional = {
            'min_level': int,
            'enabled': bool
        }

    class Category:
        required = {
            'id': str,
            'name': str
        }

    class Armor:
        required = {
            'class': int,
            'zones': List[str],
            'durability': int
        }

    class Material:
        required = {
            'name': str,
            'destructibility': float
        }

    class WeaponStats:
        required = {
            'caliber': str,
            'firerate': int,
            'ergonomics': int,
            'recoil_vertical': int,
            'recoil_horizontal': int
        }

    class Trade:
        required = {
            'id': str,
            'type': str,  # 'barter' or 'craft'
            'price_rub': float,
            'recorded_at': datetime
        }
        optional = {
            'level': int,
            'currency': str,
            'original_price': float,
            'requires_quest': bool
        }

@dataclass
class RelationshipProperties:
    class VendorPrice:
        required = {
            'price_rub': float,
            'recorded_at': datetime
        }
        optional = {
            'currency': str,
            'original_price': float,
            'requires_loyalty': int,
            'requires_quest': str
        }

    class RequiredFor:
        required = {
            'count': int,
            'recorded_at': datetime
        }
        optional = {
            'craft_station': str,
            'craft_level': int,
            'barter_only': bool
        }

    class MarketAnalysis:
        required = {
            'change_24h': float,
            'change_48h': float,
            'recorded_at': datetime
        }
        optional = {
            'volume_24h': int,
            'trades_24h': int,
            'volatility_score': float
        }

def validate_node(label: NodeLabels, properties: Dict) -> List[str]:
    """Validate node properties against the model."""
    issues = []
    model = getattr(NodeProperties, label.name, None)
    if not model:
        return [f"Unknown node label: {label.name}"]

    # Check required properties
    for prop, prop_type in model.required.items():
        if prop not in properties:
            issues.append(f"Missing required property: {prop}")
        elif not isinstance(properties[prop], prop_type):
            issues.append(f"Invalid type for {prop}: expected {prop_type.__name__}")

    # Check optional properties
    if hasattr(model, 'optional'):
        for prop, value in properties.items():
            if prop in model.optional and value is not None:
                if not isinstance(value, model.optional[prop]):
                    issues.append(f"Invalid type for optional {prop}")

    return issues

def validate_relationship(rel_type: RelationshipTypes, properties: Dict) -> List[str]:
    """Validate relationship properties against the model."""
    issues = []
    model = getattr(RelationshipProperties, rel_type.name, None)
    if not model:
        return [f"Unknown relationship type: {rel_type.name}"]

    # Check required properties
    for prop, prop_type in model.required.items():
        if prop not in properties:
            issues.append(f"Missing required property: {prop}")
        elif not isinstance(properties[prop], prop_type):
            issues.append(f"Invalid type for {prop}: expected {prop_type.__name__}")

    # Check optional properties
    if hasattr(model, 'optional'):
        for prop, value in properties.items():
            if prop in model.optional and value is not None:
                if not isinstance(value, model.optional[prop]):
                    issues.append(f"Invalid type for optional {prop}")

    return issues
