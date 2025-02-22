"""Database protocol definitions."""

from typing import Any, Protocol, TypeVar, Dict, List, Iterator, Optional
from typing_extensions import runtime_checkable
from datetime import datetime
from neo4j.work.session import Result as Neo4jResult
from neo4j import Transaction as Neo4jTransaction

T = TypeVar('T')
QueryParams = Dict[str, Any]

@runtime_checkable
class DatabaseResult(Protocol):
    def single(self) -> Optional[Dict[str, Any]]: ...
    def peek(self) -> Optional[Dict[str, Any]]: ...
    def data(self) -> List[Dict[str, Any]]: ...
    def consume(self) -> None: ...
    def keys(self) -> List[str]: ...
    def values(self) -> List[Any]: ...
    def __iter__(self) -> Iterator[Dict[str, Any]]: ...

@runtime_checkable
class DatabaseTransaction(Protocol):
    def __enter__(self) -> 'DatabaseTransaction':
        ...

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        ...

    def run(self, query: str, parameters: QueryParams = None) -> Any:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...

@runtime_checkable
class DatabaseSession(Protocol):
    def run(self, query: str, **parameters: Any) -> DatabaseResult: ...
    def close(self) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def begin_transaction(self) -> 'DatabaseTransaction': ...
    def __enter__(self) -> 'DatabaseSession': ...
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...

@runtime_checkable
class Neo4jSession(DatabaseSession, Protocol):
    def run(self, query: str, **kwargs: Any) -> Neo4jResult: ...
    def begin_transaction(self) -> Neo4jTransaction: ...
    def last_bookmark(self) -> str: ...

class Neo4jTransactionAdapter(DatabaseTransaction):
    def __init__(self, transaction: Neo4jTransaction) -> None:
        self._transaction = transaction

    def __enter__(self) -> 'Neo4jTransactionAdapter':
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()

    def run(self, query: str, parameters: QueryParams = None) -> Any:
        return self._transaction.run(query, parameters or {})

    def commit(self) -> None:
        self._transaction.commit()

    def rollback(self) -> None:
        self._transaction.rollback()

# Type variables
SessionType = TypeVar('SessionType', bound=DatabaseSession)
ResultType = TypeVar('ResultType', bound=DatabaseResult)
TransactionType = TypeVar('TransactionType', bound=DatabaseTransaction)
