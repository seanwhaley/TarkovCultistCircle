from typing import Any, Dict, List, Optional, TypeVar, Generic
import logging
from datetime import datetime

from neo4j.exceptions import ServiceUnavailable
from neo4j.graph import Graph
from neo4j.work.transaction import Transaction
from pydantic import BaseModel

from src.core.exceptions import DatabaseError, NotFoundError

logger = logging.getLogger(__name__)
ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseService(Generic[ModelType]):
    """Base service class with common database operations."""

    def __init__(self, db_session):
        self.db = db_session
        self.model_class: Optional[type[ModelType]] = None

    async def _execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        single_result: bool = False
    ) -> Any:
        """Execute a Cypher query and handle errors."""
        try:
            async with self.db.session() as session:
                result = await session.run(query, params or {})
                if single_result:
                    record = await result.single()
                    return record.data() if record else None
                return [record.data() for record in await result.fetch()]
        except ServiceUnavailable as e:
            logger.error(f"Database connection error: {str(e)}")
            raise DatabaseError("Database service is unavailable")
        except Exception as e:
            logger.error(f"Database query error: {str(e)}")
            raise DatabaseError(f"Database operation failed: {str(e)}")

    async def get_by_id(self, id: str) -> ModelType:
        """Get a single record by ID."""
        if not self.model_class:
            raise NotImplementedError("model_class must be set")

        result = await self._execute_query(
            f"MATCH (n:{self.model_class.__name__} {{uid: $id}}) RETURN n",
            {"id": id},
            single_result=True
        )
        if not result:
            raise NotFoundError(f"{self.model_class.__name__} not found")
        return self.model_class(**result)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created_at",
        order_desc: bool = True
    ) -> List[ModelType]:
        """Get all records with pagination."""
        if not self.model_class:
            raise NotImplementedError("model_class must be set")

        direction = "DESC" if order_desc else "ASC"
        result = await self._execute_query(
            f"""
            MATCH (n:{self.model_class.__name__})
            RETURN n
            ORDER BY n.{order_by} {direction}
            SKIP $skip
            LIMIT $limit
            """,
            {"skip": skip, "limit": limit}
        )
        return [self.model_class(**item) for item in result]

    async def create(self, data: Dict[str, Any]) -> ModelType:
        """Create a new record."""
        if not self.model_class:
            raise NotImplementedError("model_class must be set")

        # Add timestamps
        data["created_at"] = datetime.utcnow().isoformat()
        data["updated_at"] = data["created_at"]

        result = await self._execute_query(
            f"""
            CREATE (n:{self.model_class.__name__} $data)
            RETURN n
            """,
            {"data": data},
            single_result=True
        )
        return self.model_class(**result)

    async def update(self, id: str, data: Dict[str, Any]) -> ModelType:
        """Update an existing record."""
        if not self.model_class:
            raise NotImplementedError("model_class must be set")

        # Update timestamp
        data["updated_at"] = datetime.utcnow().isoformat()

        result = await self._execute_query(
            f"""
            MATCH (n:{self.model_class.__name__} {{uid: $id}})
            SET n += $data
            RETURN n
            """,
            {"id": id, "data": data},
            single_result=True
        )
        if not result:
            raise NotFoundError(f"{self.model_class.__name__} not found")
        return self.model_class(**result)

    async def delete(self, id: str) -> bool:
        """Delete a record."""
        if not self.model_class:
            raise NotImplementedError("model_class must be set")

        result = await self._execute_query(
            f"""
            MATCH (n:{self.model_class.__name__} {{uid: $id}})
            DELETE n
            RETURN count(n) as deleted
            """,
            {"id": id},
            single_result=True
        )
        return bool(result and result.get("deleted", 0) > 0)

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filters."""
        if not self.model_class:
            raise NotImplementedError("model_class must be set")

        where_clause = ""
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"n.{key} = ${key}")
            where_clause = "WHERE " + " AND ".join(conditions)

        result = await self._execute_query(
            f"""
            MATCH (n:{self.model_class.__name__})
            {where_clause}
            RETURN count(n) as count
            """,
            filters,
            single_result=True
        )
        return result["count"] if result else 0