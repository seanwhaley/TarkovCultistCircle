ITEMS_QUERY = """
{
  items {
    id
    name
    basePrice
    lastLowPrice
    avg24hPrice
    updated
  }
}
"""

ITEM_BY_ID_QUERY = """
query ItemById($id: ID!) {
  item(id: $id) {
    id
    name
    basePrice
    lastLowPrice
    avg24hPrice
    updated
  }
}
"""
