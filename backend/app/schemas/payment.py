"""
Payment Schemas

Request/Response models for Payment endpoints
"""

from datetime import datetime
from typing import Optional, List, Any
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.payment_log import PaymentLogResponse
from app.schemas.common import PaginationInfo


class CreatePaymentRequest(BaseModel):
    """
    Request schema for creating a new payment
    
    Used by POST /api/payments
    """
    debtor_account_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Account ID of the payer",
        examples=["ACC001"]
    )
    creditor_account_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Account ID of the payee",
        examples=["SUP001"]
    )
    transaction_amount: Decimal = Field(
        ...,
        gt=0,
        max_digits=18,
        decimal_places=2,
        description="Amount to transfer (must be positive)",
        examples=[1500.50]
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Optional payment description",
        examples=["Purchase office supplies"]
    )
    
    @field_validator('debtor_account_id', 'creditor_account_id')
    @classmethod
    def validate_account_id(cls, v: str) -> str:
        """Ensure account IDs are alphanumeric"""
        if not v.replace('_', '').isalnum():
            raise ValueError('Account ID must be alphanumeric (underscores allowed)')
        return v
    
    @field_validator('transaction_amount')
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        """Validate amount constraints"""
        if v <= 0:
            raise ValueError('Amount must be positive')
        if v > 1_000_000:
            raise ValueError('Amount exceeds maximum limit (1,000,000)')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "debtor_account_id": "ACC001",
                "creditor_account_id": "SUP001",
                "transaction_amount": 1500.50,
                "description": "Purchase office supplies"
            }
        }


class PaymentResponse(BaseModel):
    """
    Payment response schema (basic)
    
    Used for listing payments and after creation
    """
    transaction_id: str = Field(
        ...,
        description="Unique transaction identifier",
        examples=["TXN_20250118_A3F9K2"]
    )
    debtor_account_id: str = Field(
        ...,
        description="Payer account ID",
        examples=["ACC001"]
    )
    creditor_account_id: str = Field(
        ...,
        description="Payee account ID",
        examples=["SUP001"]
    )
    debtor_name: str = Field(
        ...,
        description="Payer account name",
        examples=["Main Operating Account"]
    )
    creditor_name: str = Field(
        ...,
        description="Payee account name",
        examples=["Office Supplies Ltd."]
    )
    transaction_amount: float = Field(
        ...,
        description="Transaction amount",
        examples=[1500.50]
    )
    currency: str = Field(
        default="USD",
        description="Currency code",
        examples=["USD"]
    )
    transaction_status: str = Field(
        ...,
        description="Current status: pending/processing/completed/failed",
        examples=["pending"]
    )
    description: Optional[str] = Field(
        None,
        description="Payment description",
        examples=["Purchase office supplies"]
    )
    created_at: datetime = Field(
        ...,
        description="When payment was created"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="When payment was last updated"
    )
    completed_at: Optional[datetime] = Field(
        None,
        description="When payment reached final status"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error details if status is 'failed'",
        examples=["Insufficient funds at payment gateway"]
    )
    
    @model_validator(mode='before')
    @classmethod
    def extract_account_names(cls, data: Any) -> Any:
        """Extract account names from related Account objects"""
        if isinstance(data, dict):
            return data
        
        # If data is an ORM model, extract account names
        if hasattr(data, 'debtor_account') and data.debtor_account:
            data.debtor_name = data.debtor_account.account_name
        if hasattr(data, 'creditor_account') and data.creditor_account:
            data.creditor_name = data.creditor_account.account_name
        
        return data
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "transaction_id": "TXN_20250118_A3F9K2",
                "debtor_account_id": "ACC001",
                "creditor_account_id": "SUP001",
                "debtor_name": "Main Operating Account",
                "creditor_name": "Office Supplies Ltd.",
                "transaction_amount": 1500.50,
                "currency": "USD",
                "transaction_status": "pending",
                "description": "Purchase office supplies",
                "created_at": "2025-01-18T14:30:00Z",
                "updated_at": "2025-01-18T14:30:00Z",
                "completed_at": None,
                "error_message": None
            }
        }


class PaymentDetailResponse(BaseModel):
    """
    Detailed payment response schema
    
    Used by GET /api/payments/{transaction_id}
    Includes full history of status changes
    """
    transaction_id: str = Field(..., examples=["TXN_20250118_A3F9K2"])
    debtor_account_id: str = Field(..., examples=["ACC001"])
    creditor_account_id: str = Field(..., examples=["SUP001"])
    debtor_name: str = Field(..., examples=["Main Operating Account"])
    creditor_name: str = Field(..., examples=["Office Supplies Ltd."])
    transaction_amount: float = Field(..., examples=[1500.50])
    currency: str = Field(default="USD", examples=["USD"])
    transaction_status: str = Field(..., examples=["completed"])
    description: Optional[str] = Field(None, examples=["Purchase office supplies"])
    error_message: Optional[str] = Field(None)
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    logs: List[PaymentLogResponse] = Field(
        default_factory=list,
        description="Status change history"
    )
    
    @model_validator(mode='before')
    @classmethod
    def extract_account_names(cls, data: Any) -> Any:
        """Extract account names from related Account objects"""
        if isinstance(data, dict):
            return data
        
        # If data is an ORM model, extract account names
        if hasattr(data, 'debtor_account') and data.debtor_account:
            data.debtor_name = data.debtor_account.account_name
        if hasattr(data, 'creditor_account') and data.creditor_account:
            data.creditor_name = data.creditor_account.account_name
        
        return data
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "transaction_id": "TXN_20250118_A3F9K2",
                "debtor_account_id": "ACC001",
                "creditor_account_id": "SUP001",
                "debtor_name": "Main Operating Account",
                "creditor_name": "Office Supplies Ltd.",
                "transaction_amount": 1500.50,
                "currency": "USD",
                "transaction_status": "completed",
                "description": "Purchase office supplies",
                "error_message": None,
                "created_at": "2025-01-18T14:30:00Z",
                "updated_at": "2025-01-18T14:30:08Z",
                "completed_at": "2025-01-18T14:30:08Z",
                "logs": [
                    {
                        "old_status": None,
                        "new_status": "pending",
                        "error_message": None,
                        "created_at": "2025-01-18T14:30:00Z"
                    },
                    {
                        "old_status": "pending",
                        "new_status": "processing",
                        "error_message": None,
                        "created_at": "2025-01-18T14:30:02Z"
                    },
                    {
                        "old_status": "processing",
                        "new_status": "completed",
                        "error_message": None,
                        "created_at": "2025-01-18T14:30:08Z"
                    }
                ]
            }
        }


class PaymentListResponse(BaseModel):
    """
    Paginated payment list response
    
    Used by GET /api/payments
    """
    items: List[PaymentResponse] = Field(
        default_factory=list,
        description="List of payments on current page"
    )
    pagination: PaginationInfo = Field(
        ...,
        description="Pagination metadata"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "transaction_id": "TXN_20250118_A3F9K2",
                        "debtor_account_id": "ACC001",
                        "creditor_account_id": "SUP001",
                        "transaction_amount": 1500.50,
                        "transaction_status": "completed",
                        "created_at": "2025-01-18T14:30:00Z"
                    }
                ],
                "pagination": {
                    "total": 100,
                    "page": 1,
                    "limit": 10,
                    "total_pages": 10
                }
            }
        }
