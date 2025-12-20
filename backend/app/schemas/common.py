"""
Common Schema Definitions

Shared schemas used across the API (responses, errors, pagination)
"""

from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field


# Generic type variable for API responses
T = TypeVar('T')


class ApiError(BaseModel):
    """
    Standard error response structure
    
    Used when API requests fail.
    """
    code: str = Field(
        ...,
        description="Error code (e.g., INSUFFICIENT_BALANCE, ACCOUNT_NOT_FOUND)",
        examples=["INSUFFICIENT_BALANCE"]
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
        examples=["Insufficient balance in debtor account"]
    )
    details: Optional[dict] = Field(
        None,
        description="Additional error details for debugging"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "INSUFFICIENT_BALANCE",
                "message": "Insufficient balance in debtor account",
                "details": {
                    "available_balance": 500.00,
                    "required_amount": 1500.50
                }
            }
        }


class ApiResponse(BaseModel, Generic[T]):
    """
    Standard API response wrapper
    
    All API endpoints return this structure.
    Generic type T is the actual data payload.
    """
    success: bool = Field(
        ...,
        description="Whether the request was successful"
    )
    message: Optional[str] = Field(
        None,
        description="Optional message (usually for success cases)"
    )
    data: Optional[T] = Field(
        None,
        description="Response data (present when success=true)"
    )
    error: Optional[ApiError] = Field(
        None,
        description="Error details (present when success=false)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Payment created successfully",
                "data": {"transaction_id": "TXN_20250118_A3F9K2"}
            }
        }


class PaginationInfo(BaseModel):
    """
    Pagination metadata
    
    Included in list responses to help with pagination.
    """
    total: int = Field(
        ...,
        description="Total number of items",
        examples=[100]
    )
    page: int = Field(
        ...,
        description="Current page number (1-indexed)",
        examples=[1]
    )
    limit: int = Field(
        ...,
        description="Number of items per page",
        examples=[10]
    )
    total_pages: int = Field(
        ...,
        description="Total number of pages",
        examples=[10]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "page": 1,
                "limit": 10,
                "total_pages": 10
            }
        }
