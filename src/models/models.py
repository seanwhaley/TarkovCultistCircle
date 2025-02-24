from neomodel import (
    StructuredNode, StringProperty, FloatProperty, 
    DateTimeProperty, UniqueIdProperty, RelationshipTo, 
    RelationshipFrom, IntegerProperty, ArrayProperty,
    BooleanProperty, JSONProperty
)
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(StructuredNode):
    uid = UniqueIdProperty()
    username = StringProperty(unique_index=True, required=True)
    email = StringProperty(unique_index=True, required=True)
    password_hash = StringProperty(required=True)
    created_at = DateTimeProperty(default_now=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Material(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(required=True)
    destructibility = FloatProperty(required=True)
    created_at = DateTimeProperty(default_now=True)

class Armor(StructuredNode):
    uid = UniqueIdProperty()
    class_level = IntegerProperty(required=True)
    zones = ArrayProperty(StringProperty(), required=True)
    durability = IntegerProperty(required=True)
    material = RelationshipTo('Material', 'MADE_OF')
    created_at = DateTimeProperty(default_now=True)

class WeaponStats(StructuredNode):
    uid = UniqueIdProperty()
    caliber = StringProperty(required=True)
    firerate = IntegerProperty(required=True)
    ergonomics = IntegerProperty(required=True)
    recoil_vertical = IntegerProperty(required=True)
    recoil_horizontal = IntegerProperty(required=True)
    created_at = DateTimeProperty(default_now=True)

class Item(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(required=True)
    normalized_name = StringProperty()
    category = StringProperty()
    type = StringProperty()
    base_price = FloatProperty(required=True)
    last_low_price = FloatProperty()
    avg_24h_price = FloatProperty()
    width = IntegerProperty()
    height = IntegerProperty()
    weight = FloatProperty()
    grid_image_link = StringProperty()
    wiki_link = StringProperty()
    has_grid = BooleanProperty()
    blocks_headphones = BooleanProperty()
    max_stackable = IntegerProperty()
    market_data = JSONProperty()
    updated_at = DateTimeProperty(default_now=True)
    created_at = DateTimeProperty(default_now=True)

    # Relationships
    armor = RelationshipTo('Armor', 'HAS_ARMOR')
    weapon_stats = RelationshipTo('WeaponStats', 'HAS_STATS')
    price_history = RelationshipTo('PriceHistory', 'HAD_PRICE')
    buy_from = RelationshipTo('Trade', 'CAN_BUY_FROM')
    sell_to = RelationshipTo('Trade', 'CAN_SELL_TO')
    used_in_crafts = RelationshipTo('Craft', 'USED_IN_CRAFT')
    used_in_barters = RelationshipTo('Barter', 'USED_IN_BARTER')

class PriceHistory(StructuredNode):
    uid = UniqueIdProperty()
    price_rub = FloatProperty(required=True)
    vendor_name = StringProperty(required=True)
    currency = StringProperty()
    original_price = FloatProperty()
    requires_quest = BooleanProperty()
    restock_amount = IntegerProperty()
    recorded_at = DateTimeProperty(default_now=True)
    created_at = DateTimeProperty(default_now=True)
    
    item = RelationshipFrom('Item', 'HAD_PRICE')

class Trade(StructuredNode):
    uid = UniqueIdProperty()
    trade_type = StringProperty(required=True)  # 'barter' or 'craft'
    price_rub = FloatProperty(required=True)
    level = IntegerProperty()
    currency = StringProperty()
    original_price = FloatProperty()
    requires_quest = BooleanProperty()
    created_at = DateTimeProperty(default_now=True)
    
    from_vendor = RelationshipTo('Vendor', 'FROM_VENDOR')
    to_vendor = RelationshipTo('Vendor', 'TO_VENDOR')
    item = RelationshipFrom('Item', 'CAN_BUY_FROM')

class Vendor(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(required=True, unique_index=True)
    normalized_name = StringProperty()
    min_level = IntegerProperty()
    enabled = BooleanProperty(default=True)
    created_at = DateTimeProperty(default_now=True)

class PriceOverride(StructuredNode):
    uid = UniqueIdProperty()
    new_price = FloatProperty(required=True)
    created_at = DateTimeProperty(default_now=True)
    item = RelationshipTo('Item', 'PRICE_OVERRIDE')

class BlacklistItem(StructuredNode):
    uid = UniqueIdProperty()
    created_at = DateTimeProperty(default_now=True)
    item = RelationshipTo('Item', 'BLACKLISTED')

class LockItem(StructuredNode):
    uid = UniqueIdProperty()
    created_at = DateTimeProperty(default_now=True)
    item = RelationshipTo('Item', 'LOCKED')
