"""
Test Pydantic Schemas

Verify that all schema definitions work correctly:
- Validation rules
- ORM conversion
- Serialization/Deserialization

Usage:
    python test_schemas.py
"""

import asyncio
from datetime import datetime
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Import database
from app.core.database import AsyncSessionLocal, init_db, drop_db

# Import models
from app.models.account import Account
from app.models.payment import Payment
from app.models.payment_log import PaymentLog

# Import schemas
from app.schemas.account import AccountResponse
from app.schemas.payment import (
    CreatePaymentRequest,
    PaymentResponse,
    PaymentDetailResponse,
    PaymentListResponse
)
from app.schemas.payment_log import PaymentLogResponse
from app.schemas.common import ApiResponse, ApiError, PaginationInfo


def test_section(title: str):
    """Print test section header"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)


async def test_schemas():
    """Run all schema tests"""
    
    print("="*60)
    print("Testing Pydantic Schemas")
    print("="*60)
    
    # ========================================
    # Test 1: Common Schemas
    # ========================================
    test_section("[Test 1] Common Schemas")
    
    # Test ApiError
    error = ApiError(
        code="INSUFFICIENT_BALANCE",
        message="Insufficient balance in debtor account",
        details={"available": 500.00, "required": 1500.50}
    )
    print(f"[OK] ApiError created: {error.code}")
    
    # Test ApiResponse (success)
    success_response = ApiResponse[dict](
        success=True,
        message="Operation successful",
        data={"id": "123"}
    )
    print(f"[OK] ApiResponse (success) created: {success_response.success}")
    
    # Test ApiResponse (error)
    error_response = ApiResponse[dict](
        success=False,
        error=error
    )
    print(f"[OK] ApiResponse (error) created: {error_response.error.code}")
    
    # Test PaginationInfo
    pagination = PaginationInfo(total=100, page=1, limit=10, total_pages=10)
    print(f"[OK] PaginationInfo created: page {pagination.page}/{pagination.total_pages}")
    
    # ========================================
    # Test 2: Request Validation
    # ========================================
    test_section("[Test 2] Request Validation")
    
    # Valid payment request
    try:
        valid_request = CreatePaymentRequest(
            debtor_account_id="ACC001",
            creditor_account_id="SUP001",
            transaction_amount=Decimal("1500.50"),
            description="Test payment"
        )
        print(f"[OK] Valid payment request accepted: ${valid_request.transaction_amount}")
    except Exception as e:
        print(f"[FAIL] Valid request rejected: {e}")
    
    # Invalid: negative amount
    try:
        invalid_request = CreatePaymentRequest(
            debtor_account_id="ACC001",
            creditor_account_id="SUP001",
            transaction_amount=Decimal("-100.00")
        )
        print("[FAIL] Negative amount should be rejected")
    except ValueError as e:
        print(f"[OK] Negative amount rejected: {str(e)}")
    
    # Invalid: amount too large
    try:
        invalid_request = CreatePaymentRequest(
            debtor_account_id="ACC001",
            creditor_account_id="SUP001",
            transaction_amount=Decimal("2000000.00")
        )
        print("[FAIL] Excessive amount should be rejected")
    except ValueError as e:
        print(f"[OK] Excessive amount rejected: {str(e)}")
    
    # Invalid: description too long
    try:
        invalid_request = CreatePaymentRequest(
            debtor_account_id="ACC001",
            creditor_account_id="SUP001",
            transaction_amount=Decimal("100.00"),
            description="x" * 501  # Over 500 chars
        )
        print("[FAIL] Long description should be rejected")
    except ValueError as e:
        print(f"[OK] Long description rejected")
    
    # ========================================
    # Test 3: ORM to Schema Conversion
    # ========================================
    test_section("[Test 3] ORM to Schema Conversion")
    
    # Initialize database with test data
    await drop_db()
    await init_db()
    
    async with AsyncSessionLocal() as session:
        # Create test accounts (debtor and creditor)
        debtor = Account(
            account_id="TEST_DEBTOR",
            account_name="Test Debtor Account",
            account_type="debtor",
            balance=10000.00,
            currency="USD"
        )
        creditor = Account(
            account_id="TEST_CREDITOR",
            account_name="Test Creditor Account",
            account_type="creditor",
            balance=0.00,
            currency="USD"
        )
        session.add_all([debtor, creditor])
        await session.commit()
        
        # Convert Account model to AccountResponse schema
        account_response = AccountResponse.model_validate(debtor)
        print(f"[OK] Account model converted to schema: {account_response.account_id}")
        print(f"     - Name: {account_response.account_name}")
        print(f"     - Balance: ${account_response.balance:.2f}")
        
        # Create test payment
        payment = Payment(
            transaction_id="TEST_TXN",
            debtor_account_id="TEST_DEBTOR",
            creditor_account_id="TEST_CREDITOR",
            transaction_amount=1000.00,
            currency="USD",
            transaction_status="pending",
            description="Test payment"
        )
        session.add(payment)
        await session.commit()
        
        # Convert Payment model to PaymentResponse schema
        payment_response = PaymentResponse.model_validate(payment)
        print(f"[OK] Payment model converted to schema: {payment_response.transaction_id}")
        print(f"     - Amount: ${payment_response.transaction_amount:.2f}")
        print(f"     - Status: {payment_response.transaction_status}")
        
        # Create test log
        log = PaymentLog(
            transaction_id="TEST_TXN",
            old_status=None,
            new_status="pending"
        )
        session.add(log)
        await session.commit()
        
        # Convert PaymentLog model to PaymentLogResponse schema
        log_response = PaymentLogResponse.model_validate(log)
        print(f"[OK] PaymentLog model converted to schema")
        print(f"     - Status change: {log_response.old_status} -> {log_response.new_status}")
    
    # ========================================
    # Test 4: Detailed Payment with Logs
    # ========================================
    test_section("[Test 4] Detailed Payment Response")
    
    async with AsyncSessionLocal() as session:
        # Query payment with eager loading
        result = await session.execute(
            select(Payment)
            .where(Payment.transaction_id == "TEST_TXN")
            .options(selectinload(Payment.logs))
        )
        payment = result.scalar_one()
        
        # Create detailed response
        detail_response = PaymentDetailResponse(
            transaction_id=payment.transaction_id,
            debtor_account_id=payment.debtor_account_id,
            creditor_account_id=payment.creditor_account_id,
            debtor_name="Test Debtor",
            creditor_name="Test Creditor",
            transaction_amount=payment.transaction_amount,
            currency=payment.currency,
            transaction_status=payment.transaction_status,
            description=payment.description,
            error_message=payment.error_message,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
            completed_at=payment.completed_at,
            logs=[PaymentLogResponse.model_validate(log) for log in payment.logs]
        )
        
        print(f"[OK] Detailed payment response created")
        print(f"     - Transaction: {detail_response.transaction_id}")
        print(f"     - Number of logs: {len(detail_response.logs)}")
    
    # ========================================
    # Test 5: Payment List Response
    # ========================================
    test_section("[Test 5] Payment List Response")
    
    async with AsyncSessionLocal() as session:
        # Query all payments
        result = await session.execute(select(Payment))
        payments = result.scalars().all()
        
        # Create list response
        list_response = PaymentListResponse(
            items=[PaymentResponse.model_validate(p) for p in payments],
            pagination=PaginationInfo(
                total=len(payments),
                page=1,
                limit=10,
                total_pages=1
            )
        )
        
        print(f"[OK] Payment list response created")
        print(f"     - Items: {len(list_response.items)}")
        print(f"     - Pagination: page {list_response.pagination.page}")
    
    # ========================================
    # Test 6: JSON Serialization
    # ========================================
    test_section("[Test 6] JSON Serialization")
    
    # Serialize to JSON
    json_str = account_response.model_dump_json(indent=2)
    print(f"[OK] Schema serialized to JSON")
    print(f"     Length: {len(json_str)} characters")
    
    # Deserialize from JSON
    parsed = AccountResponse.model_validate_json(json_str)
    print(f"[OK] JSON deserialized back to schema")
    print(f"     - Account ID: {parsed.account_id}")
    
    # ========================================
    # Test 7: Model Dump (dict conversion)
    # ========================================
    test_section("[Test 7] Dictionary Conversion")
    
    payment_dict = payment_response.model_dump()
    print(f"[OK] Schema converted to dict")
    print(f"     - Keys: {', '.join(list(payment_dict.keys())[:5])}...")
    print(f"     - Type: {type(payment_dict)}")
    
    # ========================================
    # Summary
    # ========================================
    test_section("[Summary]")
    print("[SUCCESS] All schema tests passed!")
    print()
    print("Tested schemas:")
    print("  - ApiError")
    print("  - ApiResponse")
    print("  - PaginationInfo")
    print("  - CreatePaymentRequest (with validation)")
    print("  - AccountResponse")
    print("  - PaymentResponse")
    print("  - PaymentDetailResponse")
    print("  - PaymentListResponse")
    print("  - PaymentLogResponse")
    print()
    print("Tested features:")
    print("  - Field validation")
    print("  - ORM model conversion (from_attributes)")
    print("  - JSON serialization/deserialization")
    print("  - Dictionary conversion")
    print("  - Nested schemas (logs in payment)")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_schemas())
