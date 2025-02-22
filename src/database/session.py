from typing import Any, Dict, Optional, TypeVar, Generic, Iterator, List
from contextlib import contextmanager
from src.database.protocols import (
    DatabaseSession,
    DatabaseResult,
    DatabaseTransaction,
)
from src.database.exceptions import TransactionError, SessionError

T = TypeVar('T', bound=DatabaseSession)

class SessionWrapper(Generic[T]):
    def __init__(self, session: T) -> None:
        self._session = session
        self._active_transaction: Optional[DatabaseTransaction] = None
        self._closed: bool = False

    def _check_state(self) -> None:
        if self._closed:
            raise SessionError("Session is closed")
        
    @contextmanager
    def transaction(self) -> Iterator[DatabaseTransaction]:
        self._check_state()
        if self._active_transaction:
            raise TransactionError("Transaction already in progress")
        
        transaction = self._session.begin_transaction()
        self._active_transaction = transaction
        try:
            yield transaction
            transaction.commit()
        except Exception:
            if transaction:
                transaction.rollback()
            raise
        finally:
            self._active_transaction = None

    def execute_query(self, query: str, **params: Any) -> DatabaseResult:
        self._check_state()
        if self._active_transaction:
            return self._active_transaction.run(query, **params)
        return self._session.run(query, **params)

    def close(self) -> None:
        if not self._closed:
            if self._active_transaction:
                self._active_transaction.rollback()
            self._session.close()
            self._closed = True

    def __enter__(self) -> T:
        return self._session

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
