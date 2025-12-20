"""
Account Schemas

Request/Response models for Account endpoints
"""

from datetime import datetime
from pydantic import BaseModel, Field


class AccountResponse(BaseModel):
    """
    Account response schema
    
    Returned by GET /api/accounts
    """
    account_id: str = Field(
        ...,
        description="Unique account identifier",
        examples=["ACC001"]
    )
    account_name: str = Field(
        ...,
        description="Display name of the account",
        examples=["Main Operating Account"]
    )
    account_type: str = Field(
        ...,
        description="Account type: 'debtor' or 'creditor'",
        examples=["debtor"]
    )
    balance: float = Field(
        ...,
        description="Current balance in USD",
        examples=[100000.00]
    )
    currency: str = Field(
        default="USD",
        description="Currency code",
        examples=["USD"]
    )
    created_at: datetime = Field(
        ...,
        description="When the account was created"
    )
    
    class Config:
        from_attributes = True  # Enable ORM mode (SQLAlchemy model conversion)
        json_schema_extra = {
            "example": {
                "account_id": "ACC001",
                "account_name": "Main Operating Account",
                "account_type": "debtor",
                "balance": 100000.00,
                "currency": "USD",
                "created_at": "2025-01-18T10:00:00Z"
            }
        }
