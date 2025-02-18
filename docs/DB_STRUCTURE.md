# Neo4j DB Structure

## Rationale

Neo4j was chosen for this project because:

1. Natural representation of item-vendor-category relationships
2. Efficient querying of complex relationships
3. Flexible schema for adding new features
4. Built-in support for temporal data (blacklists, locks)

## Node Types

### Item

Properties:

- id: string (unique identifier)
- name: string
- basePrice: integer
- weight: float
- updated: datetime
- fleaMarketFee: integer

### Vendor

Properties:

- name: string (unique)
- type: string (trader/flea)

### Category

Properties:

- name: string (unique)

### PriceOverride

Properties:

- price: integer
- created: datetime
- expires: datetime (optional)

### BlacklistEntry

Properties:

- created: datetime
- expires: datetime
- reason: string (optional)

### Lock

Properties:

- created: datetime
- expires: datetime (optional)
- priority: integer

## Relationships

```cypher
// Core Item Relationships
(Item)-[:BELONGS_TO]->(Category)
(Item)-[:SELLS_TO {price: integer}]->(Vendor)
(Item)-[:BUYABLE_FROM {price: integer}]->(Vendor)

// Feature-specific Relationships
(Item)-[:HAS_OVERRIDE]->(PriceOverride)
(Item)-[:IS_BLACKLISTED]->(BlacklistEntry)
(Item)-[:IS_LOCKED]->(Lock)
```

## Example Queries

### Finding Best Item Combinations

```cypher
MATCH (i:Item)
WHERE NOT (i)-[:IS_BLACKLISTED]->(:BlacklistEntry)
  AND i.basePrice >= 400000
RETURN i
ORDER BY i.basePrice DESC
LIMIT 5
```

### Get Active Price Overrides

```cypher
MATCH (i:Item)-[r:HAS_OVERRIDE]->(po:PriceOverride)
WHERE po.expires > datetime()
RETURN i.name, po.price
```

## Future Extensions

1. Price History Tracking

   ```cypher
   (Item)-[:PRICE_POINT]->(PriceHistory {price: int, timestamp: datetime})
   ```

2. User Preferences

   ```cypher
   (User)-[:PREFERS]->(Vendor)
   (User)-[:WATCHES]->(Item)
   ```

3. Item Relations

   ```cypher
   (Item)-[:BARTERS_FOR]->(Item)
   (Item)-[:CRAFTS_INTO]->(Item)
   ```
