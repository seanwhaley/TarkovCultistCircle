from flask import jsonify
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")

class BaseResponse(BaseModel):
    """Base response model."""
    success: bool = True
    message: Optional[str] = None

class ErrorDetail(BaseModel):
    """Error detail model."""
    loc: List[str] = Field(..., description="Location of the error")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")

class ErrorResponse(BaseResponse):
    """Error response model."""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None
    status_code: int

class DataResponse(BaseResponse, Generic[DataT]):
    """Success response with data model."""
    data: DataT

class PaginatedResponse(BaseResponse, Generic[DataT]):
    """Paginated response model."""
    data: List[DataT]
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool

class TokenResponse(BaseResponse):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    
class HealthResponse(BaseResponse):
    """Health check response model."""
    status: str
    version: str
    database_connected: bool
    redis_connected: bool
    
class ValidationResponse(ErrorResponse):
    """Validation error response model."""
    validation_errors: List[ErrorDetail]

def success_response(data, status=200):
    return jsonify({"success": True, "data": data}), status

def error_response(message, status=400):
    return jsonify({"success": False, "error": message}), status
