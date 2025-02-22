from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.core.deps import get_current_user, get_item_service
from src.models.user import User
from src.services.item_service import ItemService

router = APIRouter()

class OptimizationRequest(BaseModel):
    """Optimization request model."""
    items: List[str] = Field(..., min_items=1)
    budget: float = Field(..., gt=0)
    max_items: Optional[int] = Field(default=None, gt=0)
    min_profit: Optional[float] = Field(default=None, gt=0)

class OptimizationResult(BaseModel):
    """Optimization result model."""
    items: List[dict]
    total_cost: float
    expected_profit: float
    profit_margin: float

@router.post("/calculate", response_model=OptimizationResult)
async def calculate_optimization(
    request: OptimizationRequest,
    service: ItemService = Depends(get_item_service),
    current_user: User = Depends(get_current_user)
) -> OptimizationResult:
    """Calculate optimal item purchases within budget."""
    try:
        result = await service.optimize_purchases(
            item_ids=request.items,
            budget=request.budget,
            max_items=request.max_items,
            min_profit=request.min_profit
        )
        return OptimizationResult(
            items=result["items"],
            total_cost=result["total_cost"],
            expected_profit=result["expected_profit"],
            profit_margin=result["profit_margin"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/suggestions")
async def get_suggestions(
    budget: float = Query(..., gt=0),
    limit: int = Query(10, ge=1, le=100),
    service: ItemService = Depends(get_item_service),
    current_user: User = Depends(get_current_user)
) -> List[dict]:
    """Get investment suggestions based on budget."""
    try:
        return await service.get_investment_suggestions(
            budget=budget,
            limit=limit
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )