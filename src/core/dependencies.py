"""Flask dependency injection utilities."""
from functools import wraps
from typing import Callable, TypeVar, Any
from flask import current_app, g
from src.database.neo4j import Neo4jDB
from src.services.item_service import ItemService
from src.services.auth_service import AuthService
from src.services.tarkov_client import TarkovClient

T = TypeVar('T')

def with_db(f: Callable[..., T]) -> Callable[..., T]:
    """Decorator to inject database connection."""
    @wraps(f)
    def decorated_function(*args, **kwargs) -> T:
        if not hasattr(g, 'db'):
            g.db = Neo4jDB(
                uri=current_app.config['NEO4J_URI'],
                user=current_app.config['NEO4J_USER'],
                password=current_app.config['NEO4J_PASSWORD']
            )
        return f(db=g.db, *args, **kwargs)
    return decorated_function

def with_item_service(f: Callable[..., T]) -> Callable[..., T]:
    """Decorator to inject ItemService instance."""
    @wraps(f)
    def decorated_function(*args, **kwargs) -> T:
        if not hasattr(g, 'item_service'):
            g.item_service = ItemService(g.db if hasattr(g, 'db') else None)
        return f(service=g.item_service, *args, **kwargs)
    return decorated_function

def with_auth_service(f: Callable[..., T]) -> Callable[..., T]:
    """Decorator to inject AuthService instance."""
    @wraps(f)
    def decorated_function(*args, **kwargs) -> T:
        if not hasattr(g, 'auth_service'):
            g.auth_service = AuthService(g.db if hasattr(g, 'db') else None)
        return f(service=g.auth_service, *args, **kwargs)
    return decorated_function

def with_tarkov_client(f: Callable[..., T]) -> Callable[..., T]:
    """Decorator to inject TarkovClient instance."""
    @wraps(f)
    def decorated_function(*args, **kwargs) -> T:
        if not hasattr(g, 'tarkov_client'):
            g.tarkov_client = TarkovClient(current_app.config.get('TARKOV_API_URL'))
        return f(client=g.tarkov_client, *args, **kwargs)
    return decorated_function

def teardown_dependencies(exception: Any = None) -> None:
    """Clean up dependencies at the end of each request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()