"""
Payment Log Schemas

Request/Response models for Payment Log data
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PaymentLogResponse(BaseModel):
    """
    Payment log response schema
    
    Represents a single status change in payment history
    """
    old_status: Optional[str] = Field(
        None,
        description="Previous status (null for initial log)",
        examples=["pending"]
    )
    new_status: str = Field(
        ...,
        description="New status after change",
        examples=["processing"]
    )
    error_message: Optional[str] = Field(
        None,
        description="Error details if transitioning to 'failed'",
        examples=["Insufficient funds at payment gateway"]
    )
    created_at: datetime = Field(
        ...,
        description="When this status change occurred"
    )
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "old_status": "pending",
                "new_status": "processing",
                "error_message": None,
                "created_at": "2025-01-18T14:30:02Z"
            }
        }
