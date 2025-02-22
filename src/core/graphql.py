import requests
import logging
import os
from typing import Optional, Dict, Any
from flask import current_app
from src.graphql.queries import QUERIES, MUTATIONS

logger = logging.getLogger(__name__)

class GraphQLClient:
    def __init__(self, endpoint: Optional[str] = None):
        config = current_app.config
        self.endpoint = endpoint or config['GRAPHQL_ENDPOINT']
        self.timeout = config['API_TIMEOUT']
        self.session = requests.Session()
        self.session.timeout = self.timeout

    def execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            config = current_app.config
            headers = {
                'Authorization': f"{config['AUTH_HEADER_TYPE']} {config.get('API_KEY', '')}",
                'Content-Type': 'application/json'
            }
            response = self.session.post(
                self.endpoint,
                headers=headers,
                json={'query': query, 'variables': variables or {}}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"GraphQL query failed: {str(e)}")
            return {'errors': [{'message': str(e)}]}

    def get_items(self):
        return self.execute_query(QUERIES['GET_ITEMS'])

    def get_item(self, item_id: str):
        return self.execute_query(
            QUERIES['GET_ITEM'],
            variables={'id': item_id}
        )

    def update_price(self, item_id: str, price: float):
        return self.execute_query(
            MUTATIONS['UPDATE_PRICE'],
            variables={
                'input': {
                    'itemId': item_id,
                    'price': price
                }
            }
        )
