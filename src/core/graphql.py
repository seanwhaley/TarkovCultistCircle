import requests
import logging
import os
from typing import Optional, Dict, Any
from flask import current_app
from src.graphql.queries import QUERIES, MUTATIONS
from functools import wraps
from datetime import datetime, timedelta
from collections import OrderedDict

logger = logging.getLogger(__name__)

class LRUCache:
    """Simple LRU cache implementation."""
    def __init__(self, capacity: int = 100):
        self.cache = OrderedDict()
        self.capacity = capacity
        self._cleanup_counter = 0
        
    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None
        value, expiry = self.cache[key]
        if expiry and datetime.now() > expiry:
            del self.cache[key]
            return None
        self.cache.move_to_end(key)
        return value
        
    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        expiry = datetime.now() + timedelta(seconds=ttl) if ttl else None
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = (value, expiry)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
            
        # Periodic cleanup of expired entries
        self._cleanup_counter += 1
        if self._cleanup_counter >= 100:
            self._cleanup()
            self._cleanup_counter = 0
            
    def _cleanup(self) -> None:
        now = datetime.now()
        expired = [k for k, (_, exp) in self.cache.items() 
                  if exp and exp < now]
        for k in expired:
            del self.cache[k]

# Global cache instance
_cache = LRUCache()

class GraphQLClient:
    def __init__(self, endpoint: Optional[str] = None):
        config = current_app.config
        self.endpoint = endpoint or config['GRAPHQL_ENDPOINT']
        self.timeout = config['API_TIMEOUT']
        self.session = requests.Session()
        self.session.timeout = self.timeout

    def execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None, cache_ttl: Optional[int] = None) -> Dict[str, Any]:
        try:
            # Generate cache key if caching is enabled
            cache_key = None
            if cache_ttl is not None:
                cache_key = f"{query}:{str(variables)}"
                cached_result = _cache.get(cache_key)
                if cached_result:
                    return cached_result

            # Execute query
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
            result = response.json()

            # Cache successful results if caching is enabled
            if cache_key and cache_ttl and 'errors' not in result:
                _cache.put(cache_key, result, cache_ttl)

            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"GraphQL query failed: {str(e)}")
            return {'errors': [{'message': str(e)}]}

    def get_items(self, cache_ttl: int = 300):
        return self.execute_query(QUERIES['GET_ITEMS'], cache_ttl=cache_ttl)

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
