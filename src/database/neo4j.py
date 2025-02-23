from typing import Any, Dict, Optional, cast, ClassVar, List, Tuple, Callable, TypeVar, overload
from concurrent.futures import ThreadPoolExecutor, as_completed
from neo4j import GraphDatabase, Driver
from flask import current_app, g
import logging
from datetime import datetime
from urllib.parse import urlencode
import requests
from src.database.protocols import (
    Neo4jSession, DatabaseResult, DatabaseTransaction,
    SessionType, ResultType, TransactionType
)
from src.database.exceptions import DatabaseError, ConnectionError
from src.database.types import QueryParams, QueryResult, JsonDict
from src.config import Config

T = TypeVar('T')
logger = logging.getLogger(__name__)

class Neo4jDB:
    _instance: ClassVar[Optional['Neo4jDB']] = None
    _driver: Optional[Driver]
    _config: Dict[str, Any]
    _initialized: bool

    def __init__(self) -> None:
        self._driver = None
        self._config = {}
        self._initialized = False

    def __new__(cls) -> 'Neo4jDB':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.driver = None
        return cls._instance

    @property
    def driver(self) -> Optional[Driver]:
        return self._driver

    @driver.setter
    def driver(self, value: Optional[Driver]) -> None:
        self._driver = value

    def initialize(self, uri: str, auth_type: str = 'basic', **auth_params: QueryParams) -> None:
        if self.driver:
            return

        try:
            if auth_type == 'basic':
                self.driver = GraphDatabase.driver(
                    uri,
                    auth=(auth_params['user'], auth_params['password'])
                )
            elif auth_type == 'oauth':
                access_token = self._get_oauth_token(**auth_params)
                self.driver = GraphDatabase.driver(uri, auth=("oauth", access_token))
            else:
                raise ValueError(f"Unsupported auth type: {auth_type}")
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j connection: {str(e)}")
            raise

    def _get_oauth_token(self, **auth_params: Dict[str, Any]) -> str:
        try:
            data = {
                'grant_type': 'client_credentials',
                'client_id': auth_params['client_id'],
                'client_secret': auth_params['client_secret'],
                'scope': auth_params.get('scope', 'read write')
            }
            
            response = requests.post(
                auth_params['token_endpoint'],
                data=urlencode(data),
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if response.status_code != 200:
                raise ValueError(f"OAuth token request failed: {response.text}")
                
            token_data = response.json()
            return token_data['access_token']
            
        except Exception as e:
            logger.error(f"Failed to get OAuth token: {str(e)}")
            raise DatabaseError("Failed to authenticate with Neo4j")

    def _refresh_token(self) -> None:
        if not self._config.get('auth_type') == 'oauth':
            return
            
        try:
            new_token = self._get_oauth_token(**self._config)
            if self.driver:
                self.driver.close()
            self.driver = GraphDatabase.driver(
                self._config['uri'],
                auth=("oauth", new_token)
            )
        except Exception as e:
            logger.error(f"Failed to refresh token: {str(e)}")
            raise DatabaseError("Failed to refresh authentication token")

    def refresh_connection(self, force: bool = False) -> None:
        if not self._initialized and not force:
            return
            
        try:
            if self.driver:
                self.driver.close()
            if self._config.get('auth_type') == 'oauth':
                self._refresh_token()
            else:
                self.initialize(**self._config)
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to refresh connection: {str(e)}")
            raise ConnectionError("Failed to refresh database connection")

    def with_retry(self, max_retries: int = 3) -> None:
        for attempt in range(max_retries):
            try:
                if not self.driver or not self.driver.verify_connectivity():
                    self.refresh_connection(force=True)
                return
            except Exception as e:
                if attempt == max_retries - 1:
                    raise ConnectionError(f"Failed to establish connection after {max_retries} attempts")
                logger.warning(f"Connection attempt {attempt + 1} failed, retrying...")

    def verify_connection(self) -> bool:
        try:
            if not self.driver:
                return False
            return self.driver.verify_connectivity()
        except Exception:
            return False

    def get_session(self) -> Neo4jSession:
        if not self.driver:
            raise RuntimeError("Database not initialized")
        session = self.driver.session()
        return cast(Neo4jSession, session)

    def close(self) -> None:
        if self.driver:
            self.driver.close()
            self.driver = None

    def _execute_transaction(self, query: str, **params: Any) -> DatabaseResult:
        if not self.driver:
            raise RuntimeError("Database not initialized")
        
        with self.get_session() as session:
            with session.begin_transaction() as tx:
                result = tx.run(query, **params)
                return cast(DatabaseResult, result)

    def execute_read(self, query: str, **params: Any) -> DatabaseResult:
        try:
            return self._execute_transaction(query, **params)
        except Exception as e:
            logger.error(f"Failed to execute read query: {str(e)}")
            raise DatabaseError("Failed to execute database query")

    def execute_write(self, query: str, **params: Any) -> DatabaseResult:
        try:
            return self._execute_transaction(query, **params)
        except Exception as e:
            logger.error(f"Failed to execute write query: {str(e)}")
            raise DatabaseError("Failed to execute database query")

    def execute_transaction(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Execute a function within a transaction context."""
        if not self.driver:
            raise RuntimeError("Database not initialized")

        with self.get_session() as session:
            with session.begin_transaction() as tx:
                return func(tx, *args, **kwargs)

    def execute_batch(self, queries: List[Tuple[str, Dict[str, Any]]], batch_size: int = 1000) -> None:
        """Execute multiple queries in batches."""
        if not self.driver:
            raise RuntimeError("Database not initialized")

        with self.get_session() as session:
            with session.begin_transaction() as tx:
                for i in range(0, len(queries), batch_size):
                    batch = queries[i:i + batch_size]
                    for query, params in batch:
                        tx.run(query, **params)
                    tx.commit()

    def execute_parallel(self, queries: List[Tuple[str, Dict[str, Any]]], max_threads: int = 4) -> List[Any]:
        """Execute queries in parallel using multiple sessions."""
        if not self.driver:
            raise RuntimeError("Database not initialized")

        results: List[Any] = []
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            for query, params in queries:
                future = executor.submit(self.execute_read, query, **params)
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Query execution failed: {str(e)}")
                    raise DatabaseError("Failed to execute parallel queries")

        return results

def get_db() -> Neo4jDB:
    if 'db' not in g:
        g.db = Neo4jDB()
        if not g.db.driver:
            g.db.initialize(
                current_app.config['NEO4J_URI'],
                auth_type=current_app.config.get('NEO4J_AUTH_TYPE', 'basic'),
                user=current_app.config.get('NEO4J_USER'),
                password=current_app.config.get('NEO4J_PASSWORD')
            )
    return g.db

def close_db(e: Optional[BaseException] = None) -> None:
    db = g.pop('db', None)
    if db is not None:
        db.close()
