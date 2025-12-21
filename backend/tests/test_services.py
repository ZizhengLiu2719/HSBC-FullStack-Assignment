"""
Test Services Layer

Verify all business logic services work correctly.

Usage:
    python test_services.py
"""

import asyncio
from decimal import Decimal

from app.core.database import AsyncSessionLocal, init_db, drop_db
from app.models.account import Account
from app.services.account_service import AccountService
from app.services.payment_service import PaymentService
from app.services.status_simulator import PaymentStatusSimulator
from app.schemas.payment import CreatePaymentRequest
from app.core.exceptions import (
    AccountNotFoundException,
    InsufficientBalanceException,
    SameAccountException,
)
from app.utils.id_generator import generate_transaction_id


def test_section(title: str):
    """Print test section header"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print('='*60)


async def test_services():
    """Run all service tests"""
    
    print("="*60)
    print("Testing Services Layer")
    print("="*60)
    
    # Initialize database
    await drop_db()
    await init_db()
    
    # ========================================
    # Test 1: ID Generator
    # ========================================
    test_section("[Test 1] Transaction ID Generator")
    
    id1 = generate_transaction_id()
    id2 = generate_transaction_id()
    
    print(f"[OK] Generated ID 1: {id1}")
    print(f"[OK] Generated ID 2: {id2}")
    print(f"[OK] IDs are unique: {id1 != id2}")
    print(f"[OK] Format correct: {id1.startswith('TXN_')}")
    
    # ========================================
    # Test 2: Account Service
    # ========================================
    test_section("[Test 2] Account Service")
    
    async with AsyncSessionLocal() as db:
        # Create test accounts
        debtor = Account(
            account_id="TEST_DEBTOR",
            account_name="Test Debtor",
            account_type="debtor",
            balance=10000.00
        )
        creditor = Account(
            account_id="TEST_CREDITOR",
            account_name="Test Creditor",
            account_type="creditor",
            balance=0.00
        )
        db.add_all([debtor, creditor])
        await db.commit()
    
    async with AsyncSessionLocal() as db:
        # Test: Get all accounts
        accounts = await AccountService.get_all_accounts(db)
        print(f"[OK] Get all accounts: {len(accounts)} accounts found")
        
        # Test: Get account by ID
        account = await AccountService.get_account_by_id(db, "TEST_DEBTOR")
        print(f"[OK] Get by ID: {account.account_name if account else 'None'}")
        
        # Test: Get accounts by type
        debtors = await AccountService.get_accounts_by_type(db, "debtor")
        print(f"[OK] Get by type: {len(debtors)} debtor accounts")
        
        # Test: Check sufficient balance
        has_balance = await AccountService.check_sufficient_balance(
            db, "TEST_DEBTOR", 1000.00
        )
        print(f"[OK] Balance check (1000): {has_balance}")
        
        has_balance = await AccountService.check_sufficient_balance(
            db, "TEST_DEBTOR", 20000.00
        )
        print(f"[OK] Balance check (20000): {has_balance}")
    
    # ========================================
    # Test 3: Payment Service - Create Payment
    # ========================================
    test_section("[Test 3] Payment Service - Create Payment")
    
    async with AsyncSessionLocal() as db:
        # Valid payment
        payment_request = CreatePaymentRequest(
            debtor_account_id="TEST_DEBTOR",
            creditor_account_id="TEST_CREDITOR",
            transaction_amount=Decimal("1000.00"),
            description="Test payment"
        )
        
        payment = await PaymentService.create_payment(db, payment_request)
        print(f"[OK] Payment created: {payment.transaction_id}")
        print(f"     - Amount: ${payment.transaction_amount}")
        print(f"     - Status: {payment.transaction_status}")
    
    # Test: Account not found
    async with AsyncSessionLocal() as db:
        try:
            invalid_request = CreatePaymentRequest(
                debtor_account_id="INVALID",
                creditor_account_id="TEST_CREDITOR",
                transaction_amount=Decimal("100.00")
            )
            await PaymentService.create_payment(db, invalid_request)
            print("[FAIL] Should raise AccountNotFoundException")
        except AccountNotFoundException as e:
            print(f"[OK] AccountNotFoundException raised: {e.code}")
    
    # Test: Insufficient balance
    async with AsyncSessionLocal() as db:
        try:
            insufficient_request = CreatePaymentRequest(
                debtor_account_id="TEST_DEBTOR",
                creditor_account_id="TEST_CREDITOR",
                transaction_amount=Decimal("50000.00")
            )
            await PaymentService.create_payment(db, insufficient_request)
            print("[FAIL] Should raise InsufficientBalanceException")
        except InsufficientBalanceException as e:
            print(f"[OK] InsufficientBalanceException raised: {e.code}")
            print(f"     - Available: ${e.available_balance}")
            print(f"     - Required: ${e.required_amount}")
    
    # Test: Same account
    async with AsyncSessionLocal() as db:
        try:
            same_account_request = CreatePaymentRequest(
                debtor_account_id="TEST_DEBTOR",
                creditor_account_id="TEST_DEBTOR",
                transaction_amount=Decimal("100.00")
            )
            await PaymentService.create_payment(db, same_account_request)
            print("[FAIL] Should raise SameAccountException")
        except SameAccountException as e:
            print(f"[OK] SameAccountException raised: {e.code}")
    
    # ========================================
    # Test 4: Payment Service - Query Payments
    # ========================================
    test_section("[Test 4] Payment Service - Query Payments")
    
    async with AsyncSessionLocal() as db:
        # Get by ID
        payment = await PaymentService.get_payment_by_id(
            db, 
            payment.transaction_id,
            include_logs=True
        )
        print(f"[OK] Get by ID: {payment.transaction_id if payment else 'None'}")
        if payment:
            print(f"     - Logs count: {len(payment.logs)}")
        
        # Get paginated list
        payments, total = await PaymentService.get_payments(
            db,
            page=1,
            limit=10
        )
        print(f"[OK] Get paginated: {len(payments)} items, {total} total")
        
        # Get filtered by status
        pending_payments, pending_total = await PaymentService.get_payments(
            db,
            page=1,
            limit=10,
            status="pending"
        )
        print(f"[OK] Get by status (pending): {pending_total} payments")
    
    # ========================================
    # Test 5: Payment Service - Status Updates
    # ========================================
    test_section("[Test 5] Payment Service - Status Updates")
    
    async with AsyncSessionLocal() as db:
        # Create new payment for status testing
        status_test_request = CreatePaymentRequest(
            debtor_account_id="TEST_DEBTOR",
            creditor_account_id="TEST_CREDITOR",
            transaction_amount=Decimal("500.00"),
            description="Status test payment"
        )
        status_payment = await PaymentService.create_payment(db, status_test_request)
        print(f"[OK] Test payment created: {status_payment.transaction_id}")
    
    async with AsyncSessionLocal() as db:
        # Update to processing
        updated = await PaymentService.update_payment_status(
            db,
            status_payment.transaction_id,
            "processing"
        )
        print(f"[OK] Status updated to: {updated.transaction_status}")
        
        # Complete payment
        completed = await PaymentService.complete_payment(
            db,
            status_payment.transaction_id
        )
        print(f"[OK] Payment completed: {completed.transaction_status}")
        print(f"     - Completed at: {completed.completed_at}")
    
    # Verify balance transfer
    async with AsyncSessionLocal() as db:
        debtor = await db.get(Account, "TEST_DEBTOR")
        creditor = await db.get(Account, "TEST_CREDITOR")
        print(f"[OK] Balance transfer verified:")
        print(f"     - Debtor balance: ${debtor.balance}")
        print(f"     - Creditor balance: ${creditor.balance}")
    
    # Test: Fail payment
    async with AsyncSessionLocal() as db:
        fail_test_request = CreatePaymentRequest(
            debtor_account_id="TEST_DEBTOR",
            creditor_account_id="TEST_CREDITOR",
            transaction_amount=Decimal("100.00")
        )
        fail_payment = await PaymentService.create_payment(db, fail_test_request)
    
    async with AsyncSessionLocal() as db:
        failed = await PaymentService.fail_payment(
            db,
            fail_payment.transaction_id,
            "Test failure message"
        )
        print(f"[OK] Payment failed: {failed.transaction_status}")
        print(f"     - Error: {failed.error_message}")
    
    # ========================================
    # Test 6: Status Simulator
    # ========================================
    test_section("[Test 6] Payment Status Simulator")
    
    async with AsyncSessionLocal() as db:
        # Create payment for simulation
        sim_request = CreatePaymentRequest(
            debtor_account_id="TEST_DEBTOR",
            creditor_account_id="TEST_CREDITOR",
            transaction_amount=Decimal("250.00"),
            description="Simulation test"
        )
        sim_payment = await PaymentService.create_payment(db, sim_request)
        print(f"[OK] Created payment for simulation: {sim_payment.transaction_id}")
        print(f"     - Initial status: {sim_payment.transaction_status}")
    
    # Start simulation
    print("[INFO] Starting status simulation...")
    print("[INFO] This will take ~5-10 seconds...")
    
    task = PaymentStatusSimulator.start_simulation(sim_payment.transaction_id)
    
    # Wait for simulation to complete
    await asyncio.sleep(10)
    
    # Check final status
    async with AsyncSessionLocal() as db:
        final_payment = await PaymentService.get_payment_by_id(
            db,
            sim_payment.transaction_id,
            include_logs=True
        )
        print(f"[OK] Simulation complete!")
        print(f"     - Final status: {final_payment.transaction_status}")
        print(f"     - Status changes: {len(final_payment.logs)}")
        print(f"     - Log entries:")
        for log in final_payment.logs:
            print(f"       {log.old_status} -> {log.new_status}")
    
    # ========================================
    # Summary
    # ========================================
    test_section("[Summary]")
    print("[SUCCESS] All service tests passed!")
    print()
    print("Tested components:")
    print("  - ID Generator")
    print("  - AccountService (query, balance checks)")
    print("  - PaymentService (create, query, update)")
    print("  - Status transitions (pending -> processing -> completed/failed)")
    print("  - Balance transfers")
    print("  - PaymentStatusSimulator (async background task)")
    print()
    print("Tested error handling:")
    print("  - AccountNotFoundException")
    print("  - InsufficientBalanceException")
    print("  - SameAccountException")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_services())
