# Neo4j Database Structure

## Core Node Types

### Item

```cypher
CREATE (:Item {
    id: STRING,
    name: STRING,
    shortName: STRING,
    basePrice: INTEGER,
    updated: DATETIME,
    width: INTEGER,
    height: INTEGER,
    weight: FLOAT,
    iconLink: STRING,
    imageLink: STRING,
    wikiLink: STRING,
    changeLast24h: FLOAT,
    changeLast48h: FLOAT,
    low24h: INTEGER,
    high24h: INTEGER,
    lastLowPrice: INTEGER,
    avg24hPrice: INTEGER,
    types: LIST<STRING>
})
```

### Category

```cypher
CREATE (:Category {
    id: STRING,
    name: STRING
})
```

### Vendor

```cypher
CREATE (:Vendor {
    name: STRING,
    normalizedName: STRING,
    type: STRING  // 'trader' or 'flea'
})
```

### Task

```cypher
CREATE (:Task {
    id: STRING,
    name: STRING
})
```

### Station

```cypher
CREATE (:Station {
    id: STRING,
    name: STRING
})
```

### Trade

```cypher
CREATE (:Trade {
    id: STRING,
    type: STRING,  // 'barter' or 'craft'
    level: INTEGER,
    source: STRING,
    price: INTEGER,
    currency: STRING,
    priceRUB: INTEGER
})
```

### Material

```cypher
CREATE (:Material {
    name: STRING,
    destructibility: FLOAT
})
```

### Armor

```cypher
CREATE (:Armor {
    class: INTEGER,
    zones: LIST<STRING>,
    durability: INTEGER
})
```

### WeaponStats

```cypher
CREATE (:WeaponStats {
    caliber: STRING,
    firerate: INTEGER,
    ergonomics: INTEGER,
    recoilVertical: INTEGER,
    recoilHorizontal: INTEGER
})
```

## Relationships

### Item Category Relationships

```cypher
CREATE (i:Item)-[:IN_CATEGORY]->(c:Category)
CREATE (i:Item)-[:HAS_TYPE]->(t:ItemType)
```

### Trade Relationships

```cypher
// Buying and Selling
CREATE (i:Item)-[:CAN_BUY_FROM]->(t:Trade)-[:FROM_VENDOR]->(v:Vendor)
CREATE (i:Item)-[:CAN_SELL_TO]->(t:Trade)-[:TO_VENDOR]->(v:Vendor)

// Trade Requirements
CREATE (t:Trade)-[:REQUIRES]->(r:Requirement)

// Barters
CREATE (b:Trade {type: 'barter'})-[:REQUIRES]->(i1:Item)-[:WITH_COUNT]->(c:Count)
CREATE (b:Trade {type: 'barter'})-[:GIVES]->(i2:Item)
CREATE (b:Trade {type: 'barter'})-[:UNLOCKED_BY]->(task:Task)
CREATE (b:Trade {type: 'barter'})-[:AVAILABLE_AT]->(v:Vendor)

// Crafts
CREATE (c:Trade {type: 'craft'})-[:REQUIRES]->(i1:Item)-[:WITH_COUNT]->(count:Count)
CREATE (c:Trade {type: 'craft'})-[:PRODUCES]->(i2:Item)
CREATE (c:Trade {type: 'craft'})-[:AT_STATION]->(s:Station)
CREATE (c:Trade {type: 'craft'})-[:UNLOCKED_BY]->(task:Task)
```

### Item Properties Relationships

```cypher
// Armor Properties
CREATE (i:Item)-[:HAS_ARMOR]->(a:Armor)-[:MADE_OF]->(m:Material)

// Weapon Properties
CREATE (i:Item)-[:HAS_STATS]->(w:WeaponStats)

// Containment
CREATE (i1:Item)-[:CONTAINS {count: INTEGER}]->(i2:Item)

// Task Usage
CREATE (i:Item)-[:USED_IN]->(t:Task)-[:GIVEN_BY]->(v:Vendor)
```

## Indexes

```cypher
// Core indexes
CREATE INDEX item_id FOR (i:Item) ON (i.id)
CREATE INDEX item_name FOR (i:Item) ON (i.name)
CREATE INDEX vendor_name FOR (v:Vendor) ON (v.name)
CREATE INDEX category_id FOR (c:Category) ON (c.id)
CREATE INDEX task_id FOR (t:Task) ON (t.id)
CREATE INDEX station_name FOR (s:Station) ON (s.name)
CREATE INDEX trade_id FOR (t:Trade) ON (t.id)

// Composite indexes
CREATE INDEX item_price_idx FOR (i:Item) ON (i.basePrice, i.lastLowPrice)
CREATE INDEX trade_type_level FOR (t:Trade) ON (t.type, t.level)
```

## Constraints

```cypher
// Unique constraints
CREATE CONSTRAINT item_id_unique FOR (i:Item) REQUIRE i.id IS UNIQUE
CREATE CONSTRAINT vendor_name_unique FOR (v:Vendor) REQUIRE v.name IS UNIQUE
CREATE CONSTRAINT category_id_unique FOR (c:Category) REQUIRE c.id IS UNIQUE
CREATE CONSTRAINT task_id_unique FOR (t:Task) REQUIRE t.id IS UNIQUE
CREATE CONSTRAINT trade_id_unique FOR (t:Trade) REQUIRE t.id IS UNIQUE

// Property existence constraints
CREATE CONSTRAINT item_required_props FOR (i:Item) REQUIRE i.id IS NOT NULL
CREATE CONSTRAINT item_name_exists FOR (i:Item) REQUIRE i.name IS NOT NULL
CREATE CONSTRAINT vendor_name_exists FOR (v:Vendor) REQUIRE v.name IS NOT NULL
```

## Example Queries

### Find Best Profit Items

```cypher
MATCH (i:Item)
MATCH (i)-[:CAN_BUY_FROM]->(bt:Trade)
MATCH (i)-[:CAN_SELL_TO]->(st:Trade)
WHERE bt.priceRUB < st.priceRUB
RETURN i.name, bt.priceRUB as buyPrice, st.priceRUB as sellPrice,
       st.priceRUB - bt.priceRUB as profit
ORDER BY profit DESC
LIMIT 10
```

### Find Item Craft Profitability

```cypher
MATCH (i:Item)<-[:PRODUCES]-(c:Trade {type: 'craft'})
MATCH (c)-[:REQUIRES]->(req:Item)-[:WITH_COUNT]->(count:Count)
WITH i, c, COLLECT({item: req, count: count.value}) as requirements
MATCH (i)-[:CAN_SELL_TO]->(st:Trade)
WHERE st.priceRUB = MAX(st.priceRUB)
RETURN i.name,
       requirements,
       st.priceRUB as sellPrice,
       st.priceRUB - REDUCE(cost = 0, r IN requirements |
         cost + r.item.lastLowPrice * r.count
       ) as profit
ORDER BY profit DESC
```

### Find Items for Task

```cypher
MATCH (i:Item)-[:USED_IN]->(t:Task)-[:GIVEN_BY]->(v:Vendor)
WHERE v.name = $traderName
RETURN i.name, t.name, i.lastLowPrice
ORDER BY i.lastLowPrice DESC
```

### Get Complete Item Details

```cypher
MATCH (i:Item {id: $itemId})
OPTIONAL MATCH (i)-[:IN_CATEGORY]->(c:Category)
OPTIONAL MATCH (i)-[:HAS_ARMOR]->(a:Armor)-[:MADE_OF]->(m:Material)
OPTIONAL MATCH (i)-[:HAS_STATS]->(w:WeaponStats)
OPTIONAL MATCH (i)-[:CAN_BUY_FROM]->(bt:Trade)-[:FROM_VENDOR]->(bv:Vendor)
OPTIONAL MATCH (i)-[:CAN_SELL_TO]->(st:Trade)-[:TO_VENDOR]->(sv:Vendor)
RETURN i, c, a, m, w,
       COLLECT(DISTINCT {price: bt.priceRUB, vendor: bv.name}) as buyFrom,
       COLLECT(DISTINCT {price: st.priceRUB, vendor: sv.name}) as sellTo
```

## Optimization Notes

1. Use APOC procedures for bulk imports
2. Create appropriate indexes before bulk data loading
3. Use PERIODIC COMMIT for large data imports
4. Consider using relationship properties for counts instead of separate nodes
5. Use parameter types in Cypher queries for better performance
6. Implement proper constraints before data loading
7. Use MERGE for upsert operations during updates

## Performance Optimization Guidelines

### Query Optimization

1. Use PROFILE and EXPLAIN for query analysis
```cypher
PROFILE MATCH (i:Item)-[:IN_CATEGORY]->(:Category {name: 'Weapon'})
RETURN i.name, i.basePrice
ORDER BY i.basePrice DESC
LIMIT 10
```

2. Avoid cartesian products in queries
3. Use OPTIONAL MATCH for nullable relationships
4. Leverage parameter types for better query planning
5. Use UNWIND for batch operations

### Indexing Strategies

1. Selective Index Usage
```cypher
// High selectivity index
CREATE INDEX item_specific_type FOR (i:Item) ON (i.type) 
WHERE i.type IN ['weapon', 'armor', 'ammo']

// Composite index for price ranges
CREATE INDEX item_price_range FOR (i:Item) ON (i.basePrice, i.lastLowPrice)
WHERE i.basePrice > 50000
```

2. Index Hit Rate Monitoring
```cypher
CALL db.stats.retrieve('INDEX HITS')
YIELD hitCount, missCount
RETURN hitCount, missCount
```

### Caching Layer

1. Result Cache Configuration
```yaml
dbms.memory.pagecache.size=4G
dbms.memory.off_heap.max_size=4G
```

2. Query Plan Cache
```cypher
// Clear query cache if needed
CALL db.clearQueryCaches()
```

### Database Maintenance

1. Regular Cleanup Tasks
```cypher
// Remove orphaned nodes
MATCH (n)
WHERE NOT (n)--()
DELETE n
```

2. Database Statistics
```cypher
CALL apoc.meta.stats()
YIELD nodeCount, relCount, labels, relTypes
```

3. Periodic Index Maintenance
```cypher
CALL db.indexes() YIELD name, type, state
WHERE state <> 'ONLINE'
RETURN name, type, state
```

### Bulk Operations

1. Batch Processing
```cypher
CALL apoc.periodic.iterate(
    "MATCH (i:Item) RETURN i",
    "SET i.lastUpdated = timestamp()",
    {batchSize: 1000}
)
```

2. Memory-Efficient Updates
```cypher
USING PERIODIC COMMIT 500
LOAD CSV FROM 'file:///items.csv' AS row
MERGE (i:Item {id: row[0]})
ON CREATE SET i += {
    name: row[1],
    price: toInteger(row[2])
}
```

### Monitoring and Metrics

1. Query Runtime Metrics
```cypher
CALL apoc.monitor.kernel()
YIELD kernelStartTime, bytesRead, bytesWritten
```

2. Connection Pool Status
```cypher
CALL dbms.pool.status()
YIELD name, allocated, inUse
```

### Best Practices for Production

1. Memory Configuration
```properties
# Neo4j Memory Settings
dbms.memory.heap.initial_size=1G
dbms.memory.heap.max_size=4G
dbms.memory.pagecache.size=4G
```

2. Transaction Management
```cypher
// Use explicit transactions for critical operations
BEGIN
MATCH (i:Item {id: $itemId})
SET i.price = $newPrice
WITH i
MATCH (i)-[:HAS_HISTORY]->(h:PriceHistory)
SET h.lastUpdate = timestamp()
COMMIT
```

3. Backup Strategy
```bash
# Hot backup command
neo4j-admin backup --backup-dir=/backup/neo4j --name=full
```

### Query Examples with Performance Notes

1. Efficient Path Finding
```cypher
// Use shortest path algorithm for complex relationships
MATCH path = shortestPath((i1:Item {id: $id1})-[*]-(i2:Item {id: $id2}))
RETURN path
```

2. Aggregation Optimization
```cypher
// Use efficient aggregation with pre-sorting
MATCH (i:Item)-[:IN_CATEGORY]->(c:Category)
WITH c, collect(i.price) AS prices
RETURN c.name, 
       percentileCont(prices, 0.5) as median,
       avg(prices) as mean
ORDER BY median DESC
```

### Monitoring Queries

1. Long-Running Queries
```cypher
CALL dbms.listQueries()
YIELD queryId, elapsedTimeMillis, query
WHERE elapsedTimeMillis > 1000
RETURN queryId, elapsedTimeMillis, query
```

2. Resource Usage
```cypher
CALL dbms.queryJmx(
    "org.neo4j:instance=kernel#0,name=Memory Mapping"
)
YIELD name, attributes
RETURN name, attributes
