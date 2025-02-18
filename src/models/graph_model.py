from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

class NodeLabels(Enum):
    ITEM = "Item"
    VENDOR = "Vendor"
    CATEGORY = "Category"
    PRICE_HISTORY = "PriceHistory"
    BARTER = "Barter"
    CRAFT = "Craft"

class RelationshipTypes(Enum):
    HAD_PRICE = "HAD_PRICE"
    IN_CATEGORY = "IN_CATEGORY"
    VENDOR_BOUGHT = "VENDOR_BOUGHT"
    VENDOR_SOLD = "VENDOR_SOLD"
    USED_IN_CRAFT = "USED_IN_CRAFT"
    USED_IN_BARTER = "USED_IN_BARTER"

@dataclass
class NodeProperties:
    class Item:
        required = {
            'id': str,
            'name': str,
            'normalized_name': str,
            'base_price': str,
            'updated': str
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
            'max_stackable': int
        }

    class PriceHistory:
        required = {
            'fetched_at': datetime,
            'price_rub': str,
            'vendor_name': str
        }
        optional = {
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
            'name': str,
            'normalized_name': str
        }

    class Craft:
        required = {
            'id': str,
            'station': str,
            'level': int,
            'duration': int
        }

    class Barter:
        required = {
            'id': str,
            'trader': str,
            'level': int
        }

@dataclass
class RelationshipProperties:
    class VendorPrice:
        required = {
            'price_rub': str,
            'recorded_at': datetime,
        }
        optional = {
            'currency_code': str,
            'original_price': str,
            'requires_loyalty': int,
            'requires_quest': str,
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
            'change_48h': str,
            'change_48h_percent': str,
            'recorded_at': datetime
        }
        optional = {
            'volume_24h': int,
            'trades_24h': int,
            'volatility_score': float
        }

    class UserTracks:
        required = {
            'started_at': datetime,
        }
        optional = {
            'price_threshold': float,
            'notify_on_change': bool,
            'notes': str,
        }

def validate_node(label: NodeLabels, properties: Dict) -> List[str]:
    """Validate node properties against the model."""
    node_class = getattr(NodeProperties, label.name)
    issues = []
    
    # Check required properties
    for prop, prop_type in node_class.required.items():
        if prop not in properties:
            issues.append(f"Missing required property: {prop}")
        elif not isinstance(properties[prop], prop_type):
            issues.append(f"Invalid type for {prop}: expected {prop_type.__name__}")
    
    return issues

def validate_relationship(rel_type: RelationshipTypes, properties: Dict) -> List[str]:
    """Validate relationship properties against the model."""
    if not hasattr(RelationshipProperties, rel_type.name):
        return []
        
    rel_class = getattr(RelationshipProperties, rel_type.name)
    issues = []
    
    for prop, prop_type in rel_class.required.items():
        if prop not in properties:
            issues.append(f"Missing required property: {prop}")
        elif not isinstance(properties[prop], prop_type):
            issues.append(f"Invalid type for {prop}: expected {prop_type.__name__}")
    
    return issues
