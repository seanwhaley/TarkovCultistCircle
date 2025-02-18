# GraphQL Queries

## Fetch All Items

```graphql
query {
  items(lang: "en") {
    id
    name
    basePrice
    buyFor {
      priceRUB
      vendor {
        name
      }
    }
    # ... other fields ...
  }
}
```

## Fetch Filtered Items

```graphql
query {
  items(lang: "en", ids: ["5447a9cd4bdc2dbd208b4567"]) {
    id
    name
  }
}
