from neomodel import StructuredNode, StringProperty, FloatProperty, DateTimeProperty, UniqueIdProperty, RelationshipTo, RelationshipFrom
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

class Item(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(required=True)
    category = StringProperty()
    type = StringProperty()
    base_price = FloatProperty(required=True)
    last_low_price = FloatProperty()
    avg_24h_price = FloatProperty()
    properties = StringProperty()
    updated_at = DateTimeProperty(default_now=True)

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
