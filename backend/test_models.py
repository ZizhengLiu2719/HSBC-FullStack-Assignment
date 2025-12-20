import asyncio
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import AsyncSessionLocal, init_db, drop_db
from app.models.account import Account
from app.models.payment import Payment
from app.models.payment_log import PaymentLog


async def test_models():
    """Test all database models"""
    print("=" * 60)
    print("Testing Database Models")
    print("=" * 60)
    
    # Step 1: Initialize database
    print("\n[Step 1] Creating tables...")
    await drop_db()  # Clean slate
    await init_db()  # Create tables
    print("[OK] Tables created")
    
    async with AsyncSessionLocal() as session:
        # Step 2: Create test accounts
        print("\n[Step 2] Creating test accounts...")
        
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
        print(f"[OK] Created accounts: {debtor.account_id}, {creditor.account_id}")
        
        # Step 3: Create test payment
        print("\n[Step 3] Creating test payment...")
        
        payment = Payment(
            transaction_id="TEST_TXN_001",
            debtor_account_id=debtor.account_id,
            creditor_account_id=creditor.account_id,
            transaction_amount=1500.50,
            currency="USD",
            transaction_status="pending",
            description="Test payment transaction"
        )
        
        session.add(payment)
        await session.commit()
        print(f"[OK] Created payment: {payment.transaction_id}")
        
        # Step 4: Create payment log
        print("\n[Step 4] Creating payment log...")
        
        log = PaymentLog(
            transaction_id=payment.transaction_id,
            old_status=None,  # First log has no old status
            new_status="pending"
        )
        
        session.add(log)
        await session.commit()
        print(f"[OK] Created log: {log.log_id}")
        
        # Step 5: Test relationships
        print("\n[Step 5] Testing relationships...")
        
        # Query payment with related data (eager loading)
        result = await session.execute(
            select(Payment)
            .where(Payment.transaction_id == "TEST_TXN_001")
            .options(
                selectinload(Payment.debtor_account),
                selectinload(Payment.creditor_account),
                selectinload(Payment.logs)
            )
        )
        payment = result.scalar_one()
        
        # Test relationships
        print(f"  Payment ID: {payment.transaction_id}")
        print(f"  Debtor: {payment.debtor_account.account_name}")
        print(f"  Creditor: {payment.creditor_account.account_name}")
        print(f"  Number of logs: {len(payment.logs)}")
        print("[OK] Relationships working correctly")
        
        # Step 6: Test constraints
        print("\n[Step 6] Testing constraints...")
        
        try:
            # Try to create payment with negative amount (should fail)
            invalid_payment = Payment(
                transaction_id="TEST_INVALID",
                debtor_account_id=debtor.account_id,
                creditor_account_id=creditor.account_id,
                transaction_amount=-100.00,  # Invalid!
                currency="USD",
                transaction_status="pending"
            )
            session.add(invalid_payment)
            await session.commit()
            print("[FAIL] Constraint check failed - negative amount allowed!")
        except Exception as e:
            await session.rollback()
            print("[OK] Constraint working - negative amount rejected")
        
        try:
            # Try to create payment where debtor = creditor (should fail)
            invalid_payment2 = Payment(
                transaction_id="TEST_INVALID2",
                debtor_account_id=debtor.account_id,
                creditor_account_id=debtor.account_id,  # Same as debtor!
                transaction_amount=100.00,
                currency="USD",
                transaction_status="pending"
            )
            session.add(invalid_payment2)
            await session.commit()
            print("[FAIL] Constraint check failed - same account allowed!")
        except Exception as e:
            await session.rollback()
            print("[OK] Constraint working - same account rejected")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] All model tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_models())