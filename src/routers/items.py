from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from src.core.deps import get_current_user, get_item_service
from src.models.item import Item, ItemCreate, ItemUpdate
from src.models.user import User
from src.services.item_service import ItemService

router = APIRouter()

@router.get("/", response_model=List[Item])
async def get_items(
    skip: int = 0,
    limit: int = 100,
    service: ItemService = Depends(get_item_service),
    current_user: User = Depends(get_current_user)
) -> List[Item]:
    """Get list of items with pagination."""
    return service.get_items(skip=skip, limit=limit)

@router.get("/{item_id}", response_model=Item)
async def get_item(
    item_id: str,
    service: ItemService = Depends(get_item_service),
    current_user: User = Depends(get_current_user)
) -> Item:
    """Get a specific item by ID."""
    item = service.get_item(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    return item

@router.post("/price-override", response_model=Item)
async def price_override(
    item_id: str,
    price: float,
    service: ItemService = Depends(get_item_service),
    current_user: User = Depends(get_current_user)
) -> Item:
    """Override an item's price."""
    try:
        return service.override_price(item_id, price)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/blacklist", response_model=Item)
async def blacklist_item(
    item_id: str,
    service: ItemService = Depends(get_item_service),
    current_user: User = Depends(get_current_user)
) -> Item:
    """Blacklist an item."""
    try:
        return service.blacklist_item(item_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/lock", response_model=Item)
async def lock_item(
    item_id: str,
    service: ItemService = Depends(get_item_service),
    current_user: User = Depends(get_current_user)
) -> Item:
    """Lock an item's price."""
    try:
        return service.lock_item(item_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )