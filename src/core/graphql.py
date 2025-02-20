from typing import Dict, Any, Optional
import requests
from src.config.config import Config
from src.config.queries import ITEMS_QUERY, ITEM_BY_ID_QUERY

class GraphQLClient:
    def __init__(self, endpoint: Optional[str] = None):
        self.session = requests.Session()
        self._endpoint = endpoint or Config.GRAPHQL_ENDPOINT

    def execute_query(self, query: Optional[str] = None, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute GraphQL query and return response"""
        query = query or ITEMS_QUERY
        variables = variables or {}
        
        response = self.session.post(
            self._endpoint,
            json={'query': query, 'variables': variables},
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return response.json()

    def fetch_items(self, lang: str = 'en', item_ids: Optional[list] = None) -> Dict[str, Any]:
        """Fetch items from Tarkov API"""
        variables = {'lang': lang}
        if item_ids:
            variables['ids'] = ','.join(item_ids)
        return self.execute_query(ITEMS_QUERY, variables)

    def fetch_item(self, item_id: str, lang: str = 'en') -> Dict[str, Any]:
        """Fetch a single item by ID"""
        variables = {'id': item_id, 'lang': lang}
        return self.execute_query(ITEM_BY_ID_QUERY, variables)
