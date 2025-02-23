"""Base model definitions."""

from typing import Any, Dict, Optional, TypeVar, Generic
from datetime import datetime
from dataclasses import dataclass, field

T = TypeVar('T')

@dataclass
class BaseModel:
    """Base model for all domain models."""
    id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create model from dictionary."""
        return cls(
            id=data['id'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at'])
        )

@dataclass
class Response(Generic[T]):
    """Generic response wrapper."""
    data: Optional[T] = None
    error: Optional[str] = None
    success: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            'data': self.data,
            'error': self.error,
            'success': self.success
        }

from typing import Dict, Any

class Neo4jModel:
    """Base class for Neo4j models"""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Neo4jModel':
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__
        
    @classmethod
    def from_neo4j_result(cls, record: Dict[str, Any]) -> 'Neo4jModel':
        """Create a model instance from a Neo4j result record"""
        return cls.from_dict(record.get('properties', {}))
