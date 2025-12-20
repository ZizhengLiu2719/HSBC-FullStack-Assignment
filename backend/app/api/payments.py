"""
Payment API Endpoints

Handles payment-related HTTP requests.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.payment_service import PaymentService
from app.services.status_simulator import PaymentStatusSimulator
from app.schemas.payment import (
    CreatePaymentRequest,
    PaymentResponse,
    PaymentDetailResponse,
    PaymentListResponse
)
from app.schemas.common import ApiResponse, ApiError, PaginationInfo
from app.core.exceptions import (
    AccountNotFoundException,
    InsufficientBalanceException,
    SameAccountException,
    PaymentNotFoundException
)

# Create router
router = APIRouter(
    prefix="/api/payments",
    tags=["payments"]
)


@router.post("", response_model=ApiResponse[PaymentResponse])
async def create_payment(
    payment_data: CreatePaymentRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new payment
    
    This endpoint:
    1. Validates accounts exist
    2. Checks sufficient balance
    3. Creates payment with status 'pending'
    4. Starts background simulation task
    5. Returns immediately (non-blocking)
    
    Args:
        payment_data: Payment details
        
    Returns:
        Created payment with status 'pending'
        
    Raises:
        400 if validation fails
        404 if account not found
        
    Example:
        POST /api/payments
        Body: {
            "debtor_account_id": "ACC001",
            "creditor_account_id": "SUP001",
            "transaction_amount": 1500.50,
            "description": "Purchase office supplies"
        }
        
        Response:
        {
            "success": true,
            "data": {
                "transaction_id": "TXN_20250118_A3F9K2",
                "transaction_status": "pending",
                ...
            }
        }
    """
    try:
        # Create payment (status = pending)
        payment = await PaymentService.create_payment(db, payment_data)
        
        # Start background simulation task (non-blocking)
        PaymentStatusSimulator.start_simulation(payment.transaction_id)
        
        # Re-fetch payment with account relationships loaded
        payment_with_accounts = await PaymentService.get_payment_by_id(
            db,
            payment.transaction_id,
            include_logs=False
        )
        
        # Convert to response schema
        payment_response = PaymentResponse.model_validate(payment_with_accounts)
        
        return ApiResponse(
            success=True,
            message="Payment created successfully",
            data=payment_response
        )
        
    except AccountNotFoundException as e:
        return ApiResponse(
            success=False,
            error=ApiError(
                code=e.code,
                message=e.message,
                details={"account_id": e.account_id}
            )
        )
        
    except InsufficientBalanceException as e:
        return ApiResponse(
            success=False,
            error=ApiError(
                code=e.code,
                message=e.message,
                details={
                    "account_id": e.account_id,
                    "available_balance": e.available_balance,
                    "required_amount": e.required_amount
                }
            )
        )
        
    except SameAccountException as e:
        return ApiResponse(
            success=False,
            error=ApiError(
                code=e.code,
                message=e.message,
                details={"account_id": e.account_id}
            )
        )
        
    except Exception as e:
        return ApiResponse(
            success=False,
            error=ApiError(
                code="INTERNAL_ERROR",
                message=str(e)
            )
        )


@router.get("/{transaction_id}", response_model=ApiResponse[PaymentDetailResponse])
async def get_payment_by_id(
    transaction_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get payment details by transaction ID
    
    Returns payment with full status history (logs).
    Frontend polls this endpoint to track status changes.
    
    Args:
        transaction_id: Transaction identifier
        
    Returns:
        Payment details with logs
        
    Raises:
        404 if payment not found
        
    Example:
        GET /api/payments/TXN_20250118_A3F9K2
        
        Response:
        {
            "success": true,
            "data": {
                "transaction_id": "TXN_20250118_A3F9K2",
                "transaction_status": "processing",
                "logs": [
                    {"old_status": null, "new_status": "pending", ...},
                    {"old_status": "pending", "new_status": "processing", ...}
                ]
            }
        }
    """
    # Get payment with logs
    payment = await PaymentService.get_payment_by_id(
        db,
        transaction_id,
        include_logs=True
    )
    
    if not payment:
        return ApiResponse(
            success=False,
            error=ApiError(
                code="PAYMENT_NOT_FOUND",
                message=f"Payment '{transaction_id}' not found"
            )
        )
    
    # Convert to response schema
    payment_response = PaymentDetailResponse.model_validate(payment)
    
    return ApiResponse(
        success=True,
        data=payment_response
    )


@router.get("", response_model=ApiResponse[PaymentListResponse])
async def get_payments(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated list of payments
    
    Supports:
    - Pagination (page, limit)
    - Filtering by status
    - Ordering by created_at DESC (newest first)
    
    Args:
        page: Page number (default: 1)
        limit: Items per page (default: 10, max: 100)
        status: Filter by status (optional)
        
    Returns:
        Paginated payment list
        
    Example:
        GET /api/payments?page=1&limit=10&status=pending
        
        Response:
        {
            "success": true,
            "data": {
                "items": [...],
                "pagination": {
                    "total": 50,
                    "page": 1,
                    "limit": 10,
                    "total_pages": 5
                }
            }
        }
    """
    # Get payments from service
    payments, total_count = await PaymentService.get_payments(
        db,
        page=page,
        limit=limit,
        status=status
    )
    
    # Convert to response schemas
    payment_responses = [
        PaymentResponse.model_validate(payment)
        for payment in payments
    ]
    
    # Calculate pagination info
    import math
    total_pages = math.ceil(total_count / limit) if total_count > 0 else 1
    
    pagination_info = PaginationInfo(
        total=total_count,
        page=page,
        limit=limit,
        total_pages=total_pages
    )
    
    # Create list response
    list_response = PaymentListResponse(
        items=payment_responses,
        pagination=pagination_info
    )
    
    return ApiResponse(
        success=True,
        data=list_response
    )
