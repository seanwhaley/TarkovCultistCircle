import logging
from typing import List, Dict, Any, Optional
import aiohttp
import asyncio

from src.graphql.queries import QUERIES
from src.core.cache import cached
from src.models.item import Item

logger = logging.getLogger(__name__)

class TarkovApiService:
    """Service for interacting with the Tarkov.dev API"""
    
    def __init__(self):
        self.api_url = "https://api.tarkov.dev/graphql"
        self.timeout = 30
        
    async def _execute_query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a GraphQL query against the Tarkov.dev API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json={'query': query, 'variables': variables or {}},
                    timeout=self.timeout
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {error_text}")
                        
                    result = await response.json()
                    if 'errors' in result:
                        raise Exception(f"GraphQL errors: {result['errors']}")
                        
                    return result
        except Exception as e:
            logger.error(f"Failed to execute GraphQL query: {str(e)}")
            raise

    @cached(timeout=300)  # Cache for 5 minutes
    async def get_all_items(self) -> List[Item]:
        """Fetch all items from Tarkov.dev API"""
        try:
            result = await self._execute_query(QUERIES['GET_ITEMS'])
            items_data = result.get('data', {}).get('items', [])
            return [Item.from_api_response(item_data) for item_data in items_data]
        except Exception as e:
            logger.error(f"Failed to fetch items: {str(e)}")
            raise

    async def get_item(self, item_id: str) -> Optional[Item]:
        """Fetch a specific item by ID"""
        try:
            result = await self._execute_query(
                QUERIES['GET_ITEM'],
                variables={'id': [item_id]}
            )
            items = result.get('data', {}).get('items', [])
            return Item.from_api_response(items[0]) if items else None
        except Exception as e:
            logger.error(f"Failed to fetch item {item_id}: {str(e)}")
            raise

    async def fetch_items_by_ids(self, item_ids: List[str]) -> List[Item]:
        """Fetch multiple items by their IDs"""
        try:
            result = await self._execute_query(
                QUERIES['GET_ITEM'],
                variables={'id': item_ids}
            )
            items_data = result.get('data', {}).get('items', [])
            return [Item.from_api_response(item_data) for item_data in items_data]
        except Exception as e:
            logger.error(f"Failed to fetch items by IDs: {str(e)}")
            raise

    def sync_get_all_items(self) -> List[Item]:
        """Synchronous version of get_all_items"""
        return asyncio.run(self.get_all_items())

    def sync_get_item(self, item_id: str) -> Optional[Item]:
        """Synchronous version of get_item"""
        return asyncio.run(self.get_item(item_id))

    def sync_fetch_items_by_ids(self, item_ids: List[str]) -> List[Item]:
        """Synchronous version of fetch_items_by_ids"""
        return asyncio.run(self.fetch_items_by_ids(item_ids))