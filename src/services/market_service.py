from typing import List, Optional, Dict, Any, ClassVar, Tuple
from datetime import datetime, timedelta
import logging
from src.database.neo4j import Neo4jDB, get_db
from src.database.protocols import Neo4jSession, DatabaseResult
from src.types.responses import PriceHistoryEntry, ItemResponse
from src.services.exceptions import ValidationError, DatabaseError, ItemNotFoundError
from src.config import Config

class MarketService:
    _db: Optional[Neo4jDB]
    _logger: logging.Logger
    _update_interval: ClassVar[int] = 300
    _price_history: Dict[str, List[PriceHistoryEntry]]
    _last_update: Optional[datetime]

    def __init__(self) -> None:
        self._db = None
        self._logger = logging.getLogger(__name__)
        self._price_history = {}
        self._last_update = None

    @property
    def db(self) -> Neo4jDB:
        if self._db is None:
            self._db = get_db()
        return self._db

    def get_market_data(self, item_id: str) -> Tuple[ItemResponse, List[PriceHistoryEntry]]:
        try:
            with self.db.get_session() as session:
                result = session.run(
                    """
                    MATCH (i:Item {uid: $item_id})
                    OPTIONAL MATCH (i)-[:HAD_PRICE]->(ph:PriceHistory)
                    WHERE datetime(ph.timestamp) > datetime() - duration({days: 7})
                    RETURN i, collect(ph) as history
                    """,
                    item_id=item_id
                )
                record = result.single()
                if not record:
                    raise ItemNotFoundError(f"Item {item_id} not found")
                
                item_data = record["i"]
                history_data = record["history"]
                
                item: ItemResponse = {
                    "id": str(item_data["uid"]),
                    "name": str(item_data["name"]),
                    "price": float(item_data.get("base_price", 0.0)),
                    "blacklisted": bool(item_data.get("blacklisted", False)),
                    "locked": bool(item_data.get("locked", False))
                }
                
                history: List[PriceHistoryEntry] = [
                    {
                        "timestamp": entry["timestamp"],
                        "price": float(entry["price"]),
                        "type": str(entry["type"])
                    }
                    for entry in history_data
                ]
                
                return item, history
        except Exception as e:
            self._logger.error(f"Failed to fetch market data: {str(e)}")
            raise DatabaseError("Failed to fetch market data")

    def update_market_data(self) -> None:
        if (self._last_update and 
            datetime.utcnow() - self._last_update < timedelta(seconds=self._update_interval)):
            return

        try:
            with self.db.get_session() as session:
                session.run(
                    """
                    MATCH (i:Item)
                    WHERE i.price_override = false
                    SET i.base_price = i.base_price * (1 + rand() * 0.1 - 0.05),
                        i.last_modified = $timestamp
                    """,
                    timestamp=datetime.utcnow().isoformat()
                )
                self._last_update = datetime.utcnow()
        except Exception as e:
            self._logger.error(f"Failed to update market data: {str(e)}")
            raise DatabaseError("Failed to update market data")

    def get_price_trends(self, days: int = 7) -> Dict[str, Any]:
        try:
            with self.db.get_session() as session:
                result = session.run(
                    """
                    MATCH (i:Item)-[:HAD_PRICE]->(ph:PriceHistory)
                    WHERE datetime(ph.timestamp) > datetime() - duration({days: $days})
                    WITH i.name as item_name, collect(ph.price) as prices
                    RETURN item_name, 
                           reduce(acc = 0.0, price IN prices | acc + price) / size(prices) as avg_price,
                           min(prices) as min_price,
                           max(prices) as max_price
                    """,
                    days=days
                )
                return {"trends": [dict(record) for record in result]}
        except Exception as e:
            self._logger.error(f"Failed to fetch price trends: {str(e)}")
            raise DatabaseError("Failed to fetch price trends")
