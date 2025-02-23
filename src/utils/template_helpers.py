from typing import Dict, Any
from datetime import datetime

def format_currency(value: float) -> str:
    return f"₽{value:,.2f}"

def format_date(date: datetime) -> str:
    return date.strftime("%Y-%m-%d %H:%M:%S")

def get_pagination_info(total: int, page: int, per_page: int) -> Dict[str, Any]:
    total_pages = (total + per_page - 1) // per_page
    return {
        "total": total,
        "current_page": page,
        "per_page": per_page,
        "total_pages": total_pages
    }
