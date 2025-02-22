from typing import Dict, Any, Union, List, TypedDict, TypeVar

class QueryParams(TypedDict, total=False):
    user: str
    password: str
    client_id: str
    client_secret: str
    token_endpoint: str
    scope: str

class DatabaseConfig(TypedDict):
    uri: str
    auth_type: str
    user: str
    password: str

JsonDict = Dict[str, Any]
JsonValue = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
QueryResult = Union[JsonDict, List[JsonDict]]

T = TypeVar('T')
