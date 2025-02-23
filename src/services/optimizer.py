"""Optimized item combination calculator."""
from typing import List, Optional, Tuple
from itertools import combinations
import numpy as np
from pydantic import BaseModel

from src.models.item import Item
from src.core.logging import get_logger
from src.services.task_manager import task_queue

logger = get_logger(__name__)

class CombinationResult(BaseModel):
    """Result model for item combinations."""
    items: List[Item]
    total_buy_price: int
    total_base_price: int
    profit_margin: float

class ItemOptimizer:
    """Efficient item combination optimizer."""
    
    def __init__(self):
        self._blacklist = set()
        self._locked_items = set()
    
    def _calculate_prices(self, items: List[Item]) -> Tuple[int, int]:
        """Calculate total buy and base prices for items."""
        total_buy = sum(min(p.price_rub for p in item.buy_for) if item.buy_for else item.base_price 
                       for item in items)
        total_base = sum(item.base_price for item in items)
        return total_buy, total_base
    
    def _is_valid_combination(
        self, 
        items: List[Item], 
        min_total_value: int = 400000
    ) -> bool:
        """Check if combination meets criteria."""
        return (
            not any(item.id in self._blacklist for item in items) and
            all(locked.id in {i.id for i in items} for locked in self._locked_items)
        )
    
    async def find_optimal_combinations(
        self,
        items: List[Item],
        max_items: int = 5,
        min_total_value: int = 400000,
        max_results: int = 10
    ) -> List[CombinationResult]:
        """Find optimal item combinations efficiently."""
        # Convert items to numpy array for faster processing
        item_array = np.array(items)
        results = []
        
        # Pre-calculate prices
        base_prices = np.array([item.base_price for item in items])
        buy_prices = np.array([
            min(p.price_rub for p in item.buy_for) if item.buy_for else item.base_price 
            for item in items
        ])
        
        # Start with locked items if any
        base_combination = list(self._locked_items)
        remaining_slots = max_items - len(base_combination)
        
        if remaining_slots <= 0:
            return results
            
        # Filter eligible items
        mask = ~np.isin([item.id for item in items], 
                        [item.id for item in base_combination + list(self._blacklist)])
        eligible_items = item_array[mask]
        eligible_base_prices = base_prices[mask]
        eligible_buy_prices = buy_prices[mask]
        
        # Generate combinations in parallel chunks
        for size in range(remaining_slots, 0, -1):
            for combo_items in combinations(range(len(eligible_items)), size):
                combo_base_total = (eligible_base_prices[list(combo_items)].sum() + 
                                  sum(item.base_price for item in base_combination))
                
                if combo_base_total >= min_total_value:
                    combo_buy_total = (eligible_buy_prices[list(combo_items)].sum() + 
                                     sum(min(p.price_rub for p in item.buy_for) 
                                         if item.buy_for else item.base_price 
                                         for item in base_combination))
                    
                    full_combo = base_combination + [eligible_items[i] for i in combo_items]
                    
                    results.append(CombinationResult(
                        items=full_combo,
                        total_buy_price=int(combo_buy_total),
                        total_base_price=int(combo_base_total),
                        profit_margin=(combo_base_total - combo_buy_total) / combo_buy_total
                    ))
                    
                    if len(results) >= max_results:
                        break
            
            if results:
                break
        
        # Sort by profit margin
        results.sort(key=lambda x: x.profit_margin, reverse=True)
        return results[:max_results]
    
    def blacklist_item(self, item_id: str) -> None:
        """Add item to blacklist."""
        self._blacklist.add(item_id)
        
    def remove_from_blacklist(self, item_id: str) -> None:
        """Remove item from blacklist."""
        self._blacklist.discard(item_id)
        
    def lock_item(self, item_id: str, item: Item) -> None:
        """Lock item in combinations."""
        self._locked_items.add(item)
        
    def unlock_item(self, item_id: str) -> None:
        """Unlock item from combinations."""
        self._locked_items = {item for item in self._locked_items if item.id != item_id}

# Global optimizer instance
optimizer = ItemOptimizer()