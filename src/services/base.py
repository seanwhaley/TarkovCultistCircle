"""Base service with enhanced relationship handling."""
from typing import Any, Dict, List, Optional, TypeVar, Generic, Union
import logging
from datetime import datetime

from neo4j.exceptions import ServiceUnavailable
from pydantic import BaseModel

from src.database import db
from src.core.exceptions import DatabaseError, NotFoundError
from src.models.graph_model import NodeLabels, RelationshipTypes

logger = logging.getLogger(__name__)
ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseService(Generic[ModelType]):
    """Base service class with common database operations."""

    def __init__(self):
        self.db = db
        self.model_class: Optional[type[ModelType]] = None

    async def _execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        single_result: bool = False
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Execute a Cypher query and handle errors."""
        try:
            with self.db.session() as session:
                result = session.run(query, params or {})
                if single_result:
                    record = result.single()
                    return dict(record) if record else {}
                return [dict(record) for record in result]
        except ServiceUnavailable as e:
            logger.error(f"Database connection error: {str(e)}")
            raise DatabaseError("Database service is unavailable")
        except Exception as e:
            logger.error(f"Database query error: {str(e)}")
            raise DatabaseError(f"Database operation failed: {str(e)}")

    async def get_by_id(self, id: str) -> ModelType:
        """Get a single record by ID with relationships."""
        if not self.model_class:
            raise NotImplementedError("model_class must be set")

        result = await self._execute_query(
            f"""
            MATCH (n:{self.model_class.__name__} {{uid: $id}})
            OPTIONAL MATCH (n)-[r]->(related)
            RETURN n, collect({{type: type(r), node: related, props: properties(r)}}) as relationships
            """,
            {"id": id},
            single_result=True
        )
        if not result:
            raise NotFoundError(f"{self.model_class.__name__} not found")

        # Convert node and relationships to model
        node_data = result['n']
        node_data['relationships'] = result['relationships']
        return self.model_class(**node_data)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: str = "created_at",
        order_desc: bool = True,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get all records with pagination and filtering."""
        if not self.model_class:
            raise NotImplementedError("model_class must be set")

        # Build WHERE clause from filters
        where_clause = ""
        if filters:
            conditions = []
            for key, value in filters.items():
                if isinstance(value, (int, float)):
                    conditions.append(f"n.{key} = {value}")
                elif isinstance(value, bool):
                    conditions.append(f"n.{key} = {str(value).lower()}")
                else:
                    conditions.append(f"n.{key} = '{value}'")
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)

        direction = "DESC" if order_desc else "ASC"
        result = await self._execute_query(
            f"""
            MATCH (n:{self.model_class.__name__})
            {where_clause}
            OPTIONAL MATCH (n)-[r]->(related)
            RETURN n, collect({{type: type(r), node: related, props: properties(r)}}) as relationships
            ORDER BY n.{order_by} {direction}
            SKIP $skip
            LIMIT $limit
            """,
            {"skip": skip, "limit": limit}
        )
        
        return [
            self.model_class(**{
                **record['n'],
                'relationships': record['relationships']
            })
            for record in result
        ]

    async def create(
        self,
        data: Dict[str, Any],
        relationships: Optional[List[Dict[str, Any]]] = None
    ) -> ModelType:
        """Create a record with optional relationships."""
        if not self.model_class:
            raise NotImplementedError("model_class must be set")

        # Add timestamps
        data["created_at"] = datetime.utcnow().isoformat()
        data["updated_at"] = data["created_at"]

        # Create node
        result = await self._execute_query(
            f"""
            CREATE (n:{self.model_class.__name__} $data)
            RETURN n
            """,
            {"data": data},
            single_result=True
        )

        # Create relationships if provided
        if relationships:
            for rel in relationships:
                await self._create_relationship(
                    result['n']['uid'],
                    rel['target_id'],
                    rel['type'],
                    rel.get('properties', {})
                )

        return self.model_class(**result['n'])

    async def update(
        self,
        id: str,
        data: Dict[str, Any],
        relationships: Optional[List[Dict[str, Any]]] = None
    ) -> ModelType:
        """Update a record and its relationships."""
        if not self.model_class:
            raise NotImplementedError("model_class must be set")

        # Update timestamp
        data["updated_at"] = datetime.utcnow().isoformat()

        # Update node
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

        # Update relationships if provided
        if relationships:
            # First remove old relationships
            await self._execute_query(
                f"""
                MATCH (n:{self.model_class.__name__} {{uid: $id}})-[r]->()
                DELETE r
                """,
                {"id": id}
            )

            # Create new relationships
            for rel in relationships:
                await self._create_relationship(
                    id,
                    rel['target_id'],
                    rel['type'],
                    rel.get('properties', {})
                )

        return self.model_class(**result['n'])

    async def delete(self, id: str) -> bool:
        """Delete a record and its relationships."""
        if not self.model_class:
            raise NotImplementedError("model_class must be set")

        result = await self._execute_query(
            f"""
            MATCH (n:{self.model_class.__name__} {{uid: $id}})
            OPTIONAL MATCH (n)-[r]-()
            DELETE n, r
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
                if isinstance(value, (int, float)):
                    conditions.append(f"n.{key} = {value}")
                elif isinstance(value, bool):
                    conditions.append(f"n.{key} = {str(value).lower()}")
                else:
                    conditions.append(f"n.{key} = '{value}'")
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)

        result = await self._execute_query(
            f"""
            MATCH (n:{self.model_class.__name__})
            {where_clause}
            RETURN count(n) as count
            """,
            single_result=True
        )
        return result["count"] if result else 0

    async def _create_relationship(
        self,
        from_id: str,
        to_id: str,
        rel_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """Create a relationship between nodes."""
        await self._execute_query(
            f"""
            MATCH (a {{uid: $from_id}}), (b {{uid: $to_id}})
            CREATE (a)-[r:{rel_type} $props]->(b)
            RETURN r
            """,
            {
                "from_id": from_id,
                "to_id": to_id,
                "props": properties or {}
            }
        )