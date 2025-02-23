from typing import Generic, List, Optional, TypeVar
from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")

class Page(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

class Pagination:
    """Pagination parameter handler for FastAPI."""
    
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(50, ge=1, le=100, description="Items per page"),
        sort: Optional[str] = Query(None, description="Sort field"),
        order: Optional[str] = Query(None, pattern="^(asc|desc)$", description="Sort order")
    ):
        self.page = page
        self.size = size
        self.sort = sort
        self.order = order
        
    @property
    def skip(self) -> int:
        """Calculate number of records to skip."""
        return (self.page - 1) * self.size
        
    def get_order_by(self, default_sort: str = "created_at") -> tuple[str, bool]:
        """Get sort field and direction."""
        sort_field = self.sort or default_sort
        is_desc = self.order == "desc" if self.order else True
        return sort_field, is_desc
        
    def create_page(self, items: List[T], total: int) -> Page[T]:
        """Create a Page object from results."""
        pages = (total + self.size - 1) // self.size
        return Page(
            items=items,
            total=total,
            page=self.page,
            size=self.size,
            pages=pages,
            has_next=self.page < pages,
            has_prev=self.page > 1
        )

    def get_page_links(self, base_url: str) -> dict[str, Optional[str]]:
        """Generate pagination links."""
        links = {
            "self": f"{base_url}?page={self.page}&size={self.size}",
            "first": f"{base_url}?page=1&size={self.size}",
            "last": None,
            "next": None,
            "prev": None
        }
        
        if self.sort:
            for key in links:
                if links[key]:
                    links[key] += f"&sort={self.sort}"
                    if self.order:
                        links[key] += f"&order={self.order}"
        
        return links

def paginate(page: Pagination) -> dict:
    """Convert pagination parameters to database query parameters."""
    sort_field, is_desc = page.get_order_by()
    return {
        "skip": page.skip,
        "limit": page.size,
        "sort_field": sort_field,
        "sort_desc": is_desc
    }