import requests
from src.db import get_db, logger
from src.config import Config
from src.models.graph_model import NodeLabels, NodeProperties, RelationshipTypes

def fetch_tarkov_dev_data(query):
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'TarkovCultistCircle/1.0',
        'Accept': 'application/json'
    }
    
    payload = {
        'query': query,
        'variables': None
    }
    
    try:
        response = requests.post(
            Config.GRAPHQL_ENDPOINT,
            json=payload,
            headers=headers,
            verify=False
        )
        
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'response': response.json() if response.text else None,
            'raw_response': response.text,
            'request': {
                'headers': headers,
                'payload': payload,
                'method': 'POST',
                'url': Config.GRAPHQL_ENDPOINT
            }
        }
    except Exception as e:
        return {
            'error': str(e),
            'type': type(e).__name__,
            'request': {
                'headers': headers,
                'payload': payload,
                'method': 'POST',
                'url': Config.GRAPHQL_ENDPOINT
            }
        }

def save_items_to_neo4j(items):
    db = get_db()
    success_count = 0
    error_count = 0
    
    try:
        logger.info(f"Attempting to save {len(items)} items to Neo4j")
        
        # First, clean existing data
        try:
            db.query("MATCH (i:Item) DETACH DELETE i")
            logger.info("Cleaned existing items from database")
        except Exception as e:
            logger.error(f"Failed to clean existing items: {str(e)}")
            return False
        
        # Create items
        for item in items:
            try:
                if db.create_or_update_item(item):
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                logger.error(f"Failed to save item {item.get('id')}: {str(e)}")
                error_count += 1
        
        logger.info(f"Successfully saved {success_count} items, {error_count} failures")
        return error_count == 0
        
    except Exception as e:
        logger.error(f"Error in save_items_to_neo4j: {str(e)}")
        return False
    finally:
        db.close()

def build_graphql_query():
    """Build GraphQL query with essential fields only."""
    return """
    query {
      items(lang: en) {
        # Core Identifiers
        id
        name
        normalizedName
        shortName
        
        # Basic Market Data
        basePrice
        fleaMarketFee
        
        # Visual & Reference
        iconLink
        imageLink
        wikiLink
        backgroundColor
        gridImageLink
        types
        
        # Physical Properties
        width
        height
        weight
        hasGrid
        blocksHeadphones
        maxStackableAmount
        
        # Buy Options
        buyFor {
          priceRUB
          vendor {
            name
            normalizedName
            minLevel
            enabled
            loyalty {
              name
              level
              requiredLevel
            }
          }
          requiresQuest
          restockAmount
        }
        
        # Sell Options
        sellFor {
          priceRUB
          vendor {
            name
            normalizedName
            enabled
          }
        }
        
        # Categorization
        categories {
          id
          name
          normalizedName
        }
        
        # Crafting & Trading
        usedInTasks {
          id
          name
          trader {
            name
          }
        }
        bartersFor {
          id
          trader {
            name
          }
          level
          requiredItems {
            item {
              id
              name
              basePrice
            }
            count
          }
        }
        craftsFor {
          id
          station {
            name
            level
          }
          requiredItems {
            item {
              id
              name
              basePrice
            }
            count
          }
          rewardItems {
            item {
              id
              name
              basePrice
            }
            count
          }
          duration
        }
        
        updated
      }
    }
    """
