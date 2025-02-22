from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from src.core.neo4j import Neo4jClient
from src.services.exceptions import OptimizationError

class OptimizerService:
    """Service for handling item optimization logic"""
    
    def __init__(self):
        self.neo4j = Neo4jClient()

    def find_optimal_combinations(
        self,
        min_price: float = 400000,
        max_items: int = 5,
        include_locked: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Find optimal combinations of items based on criteria
        """
        try:
            with self.neo4j as client:
                combinations = client.find_optimal_combinations(
                    min_total=min_price,
                    max_items=max_items
                )
                
                if include_locked:
                    # Always include locked items in the results
                    locked_items = self._get_locked_items()
                    combinations = self._merge_locked_items(combinations, locked_items)
                    
                return combinations
        except Exception as e:
            raise OptimizationError(f"Failed to find optimal combinations: {str(e)}")

    def _get_locked_items(self) -> List[Dict[str, Any]]:
        """Get all currently locked items"""
        with self.neo4j as client:
            query = """
            MATCH (i:Item)
            WHERE i.locked = true AND 
                  (i.lockExpires IS NULL OR i.lockExpires > datetime())
            RETURN i
            """
            return client.query(query)

    def _merge_locked_items(
        self,
        combinations: List[Dict[str, Any]],
        locked_items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge locked items into combinations"""
        if not locked_items:
            return combinations
            
        # Include locked items in each combination
        for combo in combinations:
            combo_items = combo['items']
            locked_ids = {item['id'] for item in locked_items}
            existing_ids = {item['id'] for item in combo_items}
            
            # Add any locked items that aren't already in the combination
            for locked_item in locked_items:
                if locked_item['id'] not in existing_ids:
                    combo_items.append(locked_item)
            
            # Recalculate total price
            combo['totalPrice'] = sum(
                item.get('priceOverride', item['basePrice'])
                for item in combo_items
            )
            
        return combinations

    def save_combination(self, combination: Dict[str, Any]) -> None:
        """Save a combination for future reference"""
        try:
            with self.neo4j as client:
                client.save_combination(
                    items=[item['id'] for item in combination['items']],
                    total_price=combination['totalPrice']
                )
        except Exception as e:
            raise OptimizationError(f"Failed to save combination: {str(e)}")

    def get_saved_combinations(
        self,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get previously saved combinations"""
        try:
            with self.neo4j as client:
                query = """
                MATCH (c:Combination)
                WITH c
                ORDER BY c.created DESC
                SKIP $offset
                LIMIT $limit
                MATCH (c)-[:INCLUDES]->(i:Item)
                RETURN c.created as created,
                       c.totalPrice as totalPrice,
                       collect(i) as items
                """
                return client.query(query, {'limit': limit, 'offset': offset})
        except Exception as e:
            raise OptimizationError(f"Failed to get saved combinations: {str(e)}")