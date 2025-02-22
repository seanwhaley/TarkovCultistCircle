from typing import Protocol, Any, Dict, List, Union, Optional, runtime_checkable

@runtime_checkable
class HasID(Protocol):
    id: str

@runtime_checkable
class Identifiable(Protocol):
    def get_id(self) -> str: ...

@runtime_checkable
class Saveable(Protocol):
    def save(self) -> None: ...
    def delete(self) -> None: ...

@runtime_checkable
class DatabaseObject(HasID, Saveable, Protocol):
    """Base protocol for database objects"""
    pass
