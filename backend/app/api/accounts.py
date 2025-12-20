"""
Account API Endpoints

Handles account-related HTTP requests.
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.account_service import AccountService
from app.schemas.account import AccountResponse
from app.schemas.common import ApiResponse

# Create router
router = APIRouter(
    prefix="/api/accounts",
    tags=["accounts"]
)


@router.get("", response_model=ApiResponse[List[AccountResponse]])
async def get_all_accounts(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all accounts
    
    Returns:
        List of all accounts in the system
        
    Example:
        GET /api/accounts
        
        Response:
        {
            "success": true,
            "data": [
                {
                    "account_id": "ACC001",
                    "account_name": "Main Operating Account",
                    "account_type": "debtor",
                    "balance": 100000.00,
                    "currency": "USD",
                    "created_at": "2025-01-18T10:00:00Z"
                },
                ...
            ]
        }
    """
    accounts = await AccountService.get_all_accounts(db)
    
    # Convert to response schemas
    account_responses = [
        AccountResponse.model_validate(account)
        for account in accounts
    ]
    
    return ApiResponse(
        success=True,
        data=account_responses
    )


@router.get("/{account_id}", response_model=ApiResponse[AccountResponse])
async def get_account_by_id(
    account_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get account by ID
    
    Args:
        account_id: Account identifier
        
    Returns:
        Account details if found
        
    Raises:
        404 if account not found
        
    Example:
        GET /api/accounts/ACC001
        
        Response:
        {
            "success": true,
            "data": {
                "account_id": "ACC001",
                "account_name": "Main Operating Account",
                ...
            }
        }
    """
    from app.core.exceptions import AccountNotFoundException
    from app.schemas.common import ApiError
    
    account = await AccountService.get_account_by_id(db, account_id)
    
    if not account:
        return ApiResponse(
            success=False,
            error=ApiError(
                code="ACCOUNT_NOT_FOUND",
                message=f"Account '{account_id}' not found"
            )
        )
    
    return ApiResponse(
        success=True,
        data=AccountResponse.model_validate(account)
    )
