from typing import TypedDict, List

class PaginationInfo(TypedDict):
    page: int
    per_page: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool

class ErrorInfo(TypedDict):
    code: str
    message: str
    details: List[str]
