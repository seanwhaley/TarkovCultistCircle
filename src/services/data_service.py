from typing import List, Dict, Any, Optional
import logging
import requests
from datetime import datetime
from src.core.neo4j import Neo4jClient
from src.models.item import Item
from src.graphql.queries import QUERIES

logger = logging.getLogger(__name__)

class DataService:
    """Service for handling data operations with Tarkov.dev API and Neo4j"""
    
    def __init__(self):
        self.api_url = "https://api.tarkov.dev/graphql"
        self.timeout = 30
        self.neo4j = Neo4jClient()

    def fetch_and_store_items(self) -> Dict[str, Any]:
        """Fetch items from API and store in Neo4j"""
        try:
            # Fetch from API
            response = requests.post(
                self.api_url,
                json={'query': QUERIES['GET_ITEMS']},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            if 'errors' in data:
                raise Exception(f"GraphQL errors: {data['errors']}")
                
            items_data = data.get('data', {}).get('items', [])
            items = [Item.from_api_response(item_data) for item_data in items_data]
            
            # Store in Neo4j
            for item in items:
                with self.neo4j as client:
                    client.upsert_item(item.to_dict())
            
            return {
                'success': True,
                'message': f'Successfully imported {len(items)} items',
                'count': len(items)
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch and store items: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'count': 0
            }

    def optimize_combinations(
        self,
        min_price: float = 400000,
        max_items: int = 5
    ) -> List[Dict[str, Any]]:
        """Find optimal item combinations"""
        with self.neo4j as client:
            return client.find_optimal_combinations(
                min_total=min_price,
                max_items=max_items
            )

    def get_history(
        self,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Get combination history"""
        with self.neo4j as client:
            return client.get_combination_history(page, per_page)

    def save_combination(
        self,
        items: List[str],
        total_price: float
    ) -> str:
        """Save a combination"""
        with self.neo4j as client:
            return client.save_combination(items, total_price)

    def delete_combination(self, combination_id: str) -> None:
        """Delete a combination"""
        with self.neo4j as client:
            client.delete_combination(combination_id)

    def set_price_override(
        self,
        item_id: str,
        price: float,
        duration: Optional[int] = None
    ) -> None:
        """Set a price override"""
        with self.neo4j as client:
            client.set_price_override(item_id, price, duration)

    def set_blacklist(
        self,
        item_id: str,
        blacklisted: bool,
        duration: Optional[int] = None
    ) -> None:
        """Set item blacklist status"""
        with self.neo4j as client:
            client.set_blacklist(item_id, blacklisted, duration)

    def set_lock(
        self,
        item_id: str,
        locked: bool,
        duration: Optional[int] = None
    ) -> None:
        """Set item lock status"""
        with self.neo4j as client:
            client.set_lock(item_id, locked, duration)