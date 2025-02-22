# Tarkov.dev API Integration Guide

## Overview

This document details the integration with the Tarkov.dev GraphQL API and how data is mapped to our Neo4j database structure.

## API Endpoints

Base URL: `https://api.tarkov.dev/graphql`

## Authentication

The API is publicly accessible and does not require authentication.

## Core Queries

### Fetch All Items

```graphql
query GetItems($lang: String = "en", $ids: [ID!]) {
  items(lang: $lang, ids: $ids) {
    id
    name
    shortName
    basePrice
    updated
    # ... see queries.py for full field list
  }
}
```

### Fetch Single Item

```graphql
query GetItemById($id: ID!, $lang: String = "en") {
  item(id: $id, lang: $lang) {
    id
    name
    shortName
    basePrice
    # ... see queries.py for full field list
  }
}
```

## Data Models

### Item Properties

- Basic Properties (id, name, price)
- Physical Properties (width, height, weight)
- Market Data (prices, changes)
- Associated Content (icons, images, wiki)
- Categories and Types
- Complex Properties (armor, weapon stats)

### Relationships

- Trading (buy/sell options)
- Crafting (inputs/outputs)
- Bartering (requirements/results)
- Task Usage
- Containment (items within items)

## Neo4j Data Mapping

### Node Types

1. Item nodes - Core item data
2. Category nodes - Item categorization
3. Vendor nodes - Traders and market
4. Task nodes - Quest information
5. Trade nodes - Transaction records
6. Property nodes - Specialized attributes

### Key Relationships

1. (:Item)-[:IN_CATEGORY]->(:Category)
2. (:Item)-[:CAN_BUY_FROM]->(:Trade)-[:FROM_VENDOR]->(:Vendor)
3. (:Item)-[:CAN_SELL_TO]->(:Trade)-[:TO_VENDOR]->(:Vendor)
4. (:Item)-[:USED_IN]->(:Task)
5. (:Item)-[:CONTAINS {count: int}]->(:Item)

## Example Usage

### Find Item by ID

```graphql
query {
  item(id: "5447a9cd4bdc2dbd208b4567") {
    name
    basePrice
    buyFor {
      price
      vendor {
        name
      }
    }
  }
}
```

### Search Items by Name

```graphql
query {
  items(name: "M4A1") {
    id
    name
    basePrice
  }
}
```

### Get Item Craft Requirements

```graphql
query {
  item(id: "5447a9cd4bdc2dbd208b4567") {
    name
    craftsFor {
      station {
        name
      }
      level
      requirements {
        item {
          name
          basePrice
        }
        count
      }
    }
  }
}
```

## Data Synchronization

### Initial Import

1. Fetch all items from Tarkov.dev API
2. Create Neo4j nodes and relationships
3. Set up indexes and constraints
4. Verify data integrity

### Regular Updates

1. Poll API for changes (every 5 minutes)
2. Compare with existing data
3. Update changed properties
4. Maintain relationship consistency

## Error Handling

### API Errors

- Network timeouts: Retry with exponential backoff
- Rate limiting: Respect API limits
- Invalid responses: Log and alert

### Data Validation

- Required fields: Enforce at database level
- Relationship integrity: Use database constraints
- Price consistency: Validate before storage

## Performance Optimization

### Query Optimization

- Use appropriate indexes
- Batch related operations
- Implement caching where appropriate

### Database Efficiency

- Proper indexing strategy
- Periodic cleanup of old data
- Regular database maintenance

## Monitoring

### API Health

- Response times
- Error rates
- Data freshness

### Database Metrics

- Query performance
- Storage usage
- Relationship counts

## Development Tools

### Testing

- API mock responses
- Database fixtures
- Integration tests

### Debugging

- Query logging
- Response validation
- Error tracking

## Common Patterns

### Price Updates

```graphql
mutation {
  updatePrice(input: {
    itemId: "5447a9cd4bdc2dbd208b4567"
    price: 45000
    source: "user"
  }) {
    success
    message
  }
}
```

### Item Filtering

```graphql
query {
  items(
    types: ["weapon", "ammo"]
    minPrice: 10000
    maxPrice: 100000
  ) {
    name
    basePrice
    types
  }
}
```

## Best Practices

1. Always specify required fields
2. Use fragments for repeated field sets
3. Implement proper error handling
4. Cache appropriate responses
5. Monitor API usage
6. Validate data consistency
7. Use appropriate indexes
8. Maintain data freshness
