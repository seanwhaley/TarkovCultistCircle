"""GraphQL queries for Tarkov.dev API"""

ITEMS_QUERY = """
query GetItems($lang: String = "en", $ids: [ID!], $skipPrices: Boolean = false, $includeCategory: Boolean = true, $includeProperties: Boolean = true, $includeTrading: Boolean = true, $includeContainment: Boolean = false, $includeTasks: Boolean = false, $includeBarters: Boolean = false, $includeCrafts: Boolean = false) {
  items(lang: $lang, ids: $ids) {
    id
    name
    shortName
    basePrice @skip(if: $skipPrices)
    updated
    width
    height
    weight
    iconLink
    imageLink
    wikiLink
    changeLast24h @skip(if: $skipPrices)
    changeLast48h @skip(if: $skipPrices)
    low24h @skip(if: $skipPrices)
    high24h @skip(if: $skipPrices)
    lastLowPrice @skip(if: $skipPrices)
    avg24hPrice @skip(if: $skipPrices)
    types
    category @include(if: $includeCategory) {
      id
      name
    }
    properties @include(if: $includeProperties) {
      slots {
        filters {
          id
          name
        }
      }
      armor {
        class
        zones
        durability
        material {
          name
          destructibility
        }
      }
      weaponStats {
        caliber
        firerate
        ergonomics
        recoilVertical
        recoilHorizontal
      }
    }
    buyFor @include(if: $includeTrading) {
      source
      price
      currency
      priceRUB
      vendor {
        name
        normalizedName
      }
      requirements {
        type
        value
      }
    }
    sellFor @include(if: $includeTrading) {
      source
      price
      currency
      priceRUB
      vendor {
        name
        normalizedName
      }
      requirements {
        type
        value
      }
    }
    containsItems @include(if: $includeContainment) {
      item {
        id
        name
      }
      count
    }
    usedInTasks @include(if: $includeTasks) {
      id
      name
      trader {
        name
      }
    }
    bartersFor @include(if: $includeBarters) {
      id
      trader {
        name
      }
      level
      taskUnlock {
        id
        name
      }
    }
    bartersUsing @include(if: $includeBarters) {
      id
      trader {
        name
      }
      level
      taskUnlock {
        id
        name
      }
    }
    craftsFor @include(if: $includeCrafts) {
      id
      station {
        name
      }
      level
      taskUnlock {
        id
        name
      }
    }
    craftsUsing @include(if: $includeCrafts) {
      id
      station {
        name
      }
      level
      taskUnlock {
        id
        name
      }
    }
  }
}
"""

ITEM_BY_ID_QUERY = """
query GetItemById($id: ID!, $lang: String = "en", $skipPrices: Boolean = false, $includeCategory: Boolean = true, $includeProperties: Boolean = true, $includeTrading: Boolean = true, $includeContainment: Boolean = false, $includeTasks: Boolean = false, $includeBarters: Boolean = false, $includeCrafts: Boolean = false) {
  item(id: $id, lang: $lang) {
    ... ItemFields
  }
}

fragment ItemFields on Item {
  id
  name
  shortName
  basePrice @skip(if: $skipPrices)
  updated
  width
  height
  weight
  iconLink
  imageLink
  wikiLink
  changeLast24h @skip(if: $skipPrices)
  changeLast48h @skip(if: $skipPrices)
  low24h @skip(if: $skipPrices)
  high24h @skip(if: $skipPrices)
  lastLowPrice @skip(if: $skipPrices)
  avg24hPrice @skip(if: $skipPrices)
  types
  category @include(if: $includeCategory) {
    id
    name
  }
  properties @include(if: $includeProperties) {
    slots {
      filters {
        id
        name
      }
    }
    armor {
      class
      zones
      durability
      material {
        name
        destructibility
      }
    }
    weaponStats {
      caliber
      firerate
      ergonomics
      recoilVertical
      recoilHorizontal
    }
  }
  buyFor @include(if: $includeTrading) {
    source
    price
    currency
    priceRUB
    vendor {
      name
      normalizedName
    }
    requirements {
      type
      value
    }
  }
  sellFor @include(if: $includeTrading) {
    source
    price
    currency
    priceRUB
    vendor {
      name
      normalizedName
    }
    requirements {
      type
      value
    }
  }
  containsItems @include(if: $includeContainment) {
    item {
      id
      name
    }
    count
  }
  usedInTasks @include(if: $includeTasks) {
    id
    name
    trader {
      name
    }
  }
  bartersFor @include(if: $includeBarters) {
    id
    trader {
      name
    }
    level
    taskUnlock {
      id
      name
    }
  }
  bartersUsing @include(if: $includeBarters) {
    id
    trader {
      name
    }
    level
    taskUnlock {
      id
      name
    }
  }
  craftsFor @include(if: $includeCrafts) {
    id
    station {
      name
    }
    level
    taskUnlock {
      id
      name
    }
  }
  craftsUsing @include(if: $includeCrafts) {
    id
    station {
      name
    }
    level
    taskUnlock {
      id
      name
    }
  }
}

# Default query variables
DEFAULT_QUERY_VARIABLES = {
    "skipPrices": False,
    "includeCategory": True,
    "includeProperties": True,
    "includeTrading": True,
    "includeContainment": False,
    "includeTasks": False,
    "includeBarters": False,
    "includeCrafts": False
}
"""
