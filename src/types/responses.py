from typing import TypedDict, Union, Dict, Any, List, Tuple, Optional
from flask import Response
from werkzeug.wrappers.response import Response as WerkzeugResponse

JsonDict = Dict[str, Any]
JsonValue = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]

class ItemBase(TypedDict, total=True):
    id: str
    name: str
    price: float
    blacklisted: bool
    locked: bool

class ItemResponse(ItemBase, total=False):
    last_modified: str

class PriceHistoryEntry(TypedDict, total=True):
    timestamp: str
    price: float
    type: str

class PaginatedResponse(TypedDict):
    items: List[ItemResponse]
    total: int
    page: int
    per_page: int
    pages: int

class ErrorResponse(TypedDict):
    error: str
    details: Optional[Dict[str, Any]]

class SuccessResponse(TypedDict):
    message: str
    data: Optional[Any]

APIResponse = Union[ErrorResponse, SuccessResponse]
JsonResponse = Dict[str, Any]
FlaskResponse = Union[Response, WerkzeugResponse, str, JsonResponse]
ResponseType = Union[FlaskResponse, Tuple[FlaskResponse, int]]
