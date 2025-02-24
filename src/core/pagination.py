"""Flask pagination utilities."""
from typing import TypeVar, Generic, List, Optional, Dict
from dataclasses import dataclass
from flask import request, url_for

T = TypeVar('T')

@dataclass
class Page(Generic[T]):
    """Pagination result container."""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

class Pagination:
    """Pagination parameter handler for Flask."""
    
    def __init__(
        self,
        page: int = 1,
        size: int = 20,
        max_size: int = 100,
        sort: Optional[str] = None,
        order: Optional[str] = None
    ):
        self.page = max(1, page)
        self.size = min(max_size, max(1, size))
        self.sort = sort
        self.order = order if order in ('asc', 'desc') else None
        
    @classmethod
    def from_request(cls) -> 'Pagination':
        """Create pagination from Flask request args."""
        return cls(
            page=request.args.get('page', 1, type=int),
            size=request.args.get('size', 20, type=int),
            sort=request.args.get('sort'),
            order=request.args.get('order')
        )
        
    def get_skip(self) -> int:
        """Get number of items to skip."""
        return (self.page - 1) * self.size
        
    def get_page_links(self, endpoint: str, **kwargs) -> Dict[str, Optional[str]]:
        """Generate pagination links using Flask url_for."""
        links = {
            "self": url_for(
                endpoint,
                page=self.page,
                size=self.size,
                **kwargs,
                _external=True
            ),
            "first": url_for(
                endpoint,
                page=1,
                size=self.size,
                **kwargs,
                _external=True
            ),
            "last": None,
            "next": None,
            "prev": None
        }
        
        if self.sort:
            for key in links:
                if links[key]:
                    links[key] = f"{links[key]}&sort={self.sort}"
                    if self.order:
                        links[key] = f"{links[key]}&order={self.order}"
        
        return links
        
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