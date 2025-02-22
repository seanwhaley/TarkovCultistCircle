"""Tarkov.dev API client service."""
from typing import List, Optional
import httpx
from gql import Client, gql
from gql.transport.httpx import HTTPXTransport

from src.models.item import Item
from src.core.cache import cached

class TarkovClient:
    """Client for interacting with Tarkov.dev GraphQL API."""
    
    def __init__(self, api_url: str = "https://api.tarkov.dev/graphql"):
        transport = HTTPXTransport(url=api_url)
        self.client = Client(
            transport=transport,
            fetch_schema_from_transport=True
        )
        
    @cached(timeout=300)  # Cache for 5 minutes
    async def get_items(self, lang: str = "en") -> List[Item]:
        """Fetch items from Tarkov.dev API."""
        query = gql("""
            query GetItems($lang: String!) {
                items(lang: $lang) {
                    id
                    name
                    basePrice
                    buyFor {
                        priceRUB
                        vendor {
                            name
                        }
                    }
                    categories {
                        name
                    }
                    fleaMarketFee
                    sellFor {
                        priceRUB
                        vendor {
                            name
                        }
                    }
                    updated
                    weight
                }
            }
        """)
        
        result = await self.client.execute_async(
            query,
            variable_values={"lang": lang}
        )
        
        return [Item.model_validate(item) for item in result["items"]]
    
    async def get_item_by_id(self, item_id: str, lang: str = "en") -> Optional[Item]:
        """Fetch a specific item by ID."""
        query = gql("""
            query GetItem($id: ID!, $lang: String!) {
                item(id: $id, lang: $lang) {
                    id
                    name
                    basePrice
                    buyFor {
                        priceRUB
                        vendor { name }
                    }
                    categories { name }
                    fleaMarketFee
                    sellFor {
                        priceRUB
                        vendor { name }
                    }
                    updated
                    weight
                }
            }
        """)
        
        try:
            result = await self.client.execute_async(
                query,
                variable_values={"id": item_id, "lang": lang}
            )
            return Item.model_validate(result["item"]) if result.get("item") else None
        except Exception:
            return None