from typing import Protocol, Any, TypeVar, Dict, Union, Iterator
from neo4j.work.session import Result

class Neo4jSession(Protocol):
    def run(self, query: str, **kwargs: Any) -> Result: ...
    def close(self) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...

class Neo4jResult(Protocol):
    def single(self) -> Any: ...
    def data(self) -> List[Dict[str, Any]]: ...
    def consume(self) -> Any: ...
    def peek(self) -> Any: ...
    def __iter__(self) -> Iterator[Any]: ...

SessionType = TypeVar('SessionType', bound=Neo4jSession)
