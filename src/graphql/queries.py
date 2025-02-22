"""GraphQL queries for the Tarkov.dev API"""

QUERIES = {
    'GET_ITEMS': """
    query GetItems {
        items {
            id
            name
            normalizedName
            shortName
            basePrice
            width
            height
            iconLink
            gridImageLink
            baseImageLink
            types
            updated
            properties {
                ... on ItemPropertiesAmmo {
                    damage
                    penetrationPower
                }
                ... on ItemPropertiesArmor {
                    class
                    durability
                    material {
                        name
                    }
                }
            }
            sellFor {
                price
                currency
                vendor {
                    name
                }
            }
            buyFor {
                price
                currency
                vendor {
                    name
                }
            }
        }
    }
    """,
    
    'GET_ITEM': """
    query GetItem($id: [ID!]) {
        items(ids: $id) {
            id
            name
            normalizedName
            shortName
            basePrice
            width
            height
            iconLink
            gridImageLink
            baseImageLink
            types
            updated
            properties {
                ... on ItemPropertiesAmmo {
                    damage
                    penetrationPower
                }
                ... on ItemPropertiesArmor {
                    class
                    durability
                    material {
                        name
                    }
                }
            }
            sellFor {
                price
                currency
                vendor {
                    name
                }
            }
            buyFor {
                price
                currency
                vendor {
                    name
                }
            }
        }
    }
    """,
    
    'GET_ITEMS_BY_TYPE': """
    query GetItemsByType($type: String!) {
        items(type: $type) {
            id
            name
            normalizedName
            shortName
            basePrice
            width
            height
            iconLink
            gridImageLink
            types
            updated
            sellFor {
                price
                currency
                vendor {
                    name
                }
            }
            buyFor {
                price
                currency
                vendor {
                    name
                }
            }
        }
    }
    """
}

MUTATIONS = {
    'UPDATE_PRICE_OVERRIDE': """
        mutation UpdatePriceOverride($itemId: String!, $price: Float!, $duration: Int) {
            updatePriceOverride(itemId: $itemId, price: $price, duration: $duration) {
                success
                message
            }
        }
    """,
    'UPDATE_BLACKLIST': """
        mutation UpdateBlacklist($itemId: String!, $blacklisted: Boolean!, $duration: Int) {
            updateBlacklist(itemId: $itemId, blacklisted: $blacklisted, duration: $duration) {
                success
                message
            }
        }
    """,
    'UPDATE_LOCK': """
        mutation UpdateLock($itemId: String!, $locked: Boolean!, $duration: Int) {
            updateLock(itemId: $itemId, locked: $locked, duration: $duration) {
                success
                message
            }
        }
    """
}
