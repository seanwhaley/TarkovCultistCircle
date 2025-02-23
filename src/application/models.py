from typing import Optional, Dict, Any

class Item:
    def __init__(self, data: Dict[str, Any]):
        self.id: str = data.get('id', '')
        self.name: str = data.get('name', '')
        self.base_price: int = data.get('basePrice', 0)
        self.last_low_price: int = data.get('lastLowPrice', 0)
        self.avg_24h_price: int = data.get('avg24hPrice', 0)
        self.updated: str = data.get('updated', '')
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'basePrice': self.base_price,
            'lastLowPrice': self.last_low_price,
            'avg24hPrice': self.avg_24h_price,
            'updated': self.updated
        }
        
    @classmethod
    def from_neo4j_result(cls, record: Dict[str, Any]) -> 'Item':
        """Create an Item instance from a Neo4j result record"""
        return cls(record.get('properties', {}))

    def __repr__(self) -> str:
        return f"<Item(name={self.name}, basePrice={self.base_price})>"
