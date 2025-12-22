"""
Payment Service

Handles payment-related business logic.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.payment import Payment
from app.models.payment_log import PaymentLog
from app.models.account import Account
from app.schemas.payment import CreatePaymentRequest
from app.core.exceptions import (
    AccountNotFoundException,
    InsufficientBalanceException,
    SameAccountException,
    PaymentNotFoundException,
)
from app.utils.id_generator import generate_transaction_id


class PaymentService:
    """
    Service for payment operations
    
    Responsibilities:
    - Create payments
    - Query payments
    - Update payment status
    - Manage payment logs
    - Handle balance transfers
    """
    
    @staticmethod
    async def create_payment(
        db: AsyncSession,
        payment_data: CreatePaymentRequest
    ) -> Payment:
        """
        Create a new payment transaction
        
        Steps:
        1. Validate accounts exist
        2. Check accounts are different
        3. Verify sufficient balance
        4. Create payment record
        5. Create initial log entry
        
        Args:
            db: Database session
            payment_data: Payment request data
            
        Returns:
            Created payment object
            
        Raises:
            AccountNotFoundException: If either account doesn't exist
            SameAccountException: If debtor and creditor are the same
            InsufficientBalanceException: If balance is insufficient
        """
        # Step 1: Validate debtor account exists
        debtor = await db.get(Account, payment_data.debtor_account_id)
        if not debtor:
            raise AccountNotFoundException(payment_data.debtor_account_id)
        
        # Step 2: Validate creditor account exists
        creditor = await db.get(Account, payment_data.creditor_account_id)
        if not creditor:
            raise AccountNotFoundException(payment_data.creditor_account_id)
        
        # Step 3: Check accounts are different
        if payment_data.debtor_account_id == payment_data.creditor_account_id:
            raise SameAccountException(payment_data.debtor_account_id)
        
        # Step 4: Verify sufficient balance
        required_amount = float(payment_data.transaction_amount)
        if debtor.balance < required_amount:
            raise InsufficientBalanceException(
                account_id=payment_data.debtor_account_id,
                available=debtor.balance,
                required=required_amount
            )
        
        # Step 5: Generate transaction ID
        transaction_id = generate_transaction_id()
        
        # Step 6: Create payment record
        payment = Payment(
            transaction_id=transaction_id,
            debtor_account_id=payment_data.debtor_account_id,
            creditor_account_id=payment_data.creditor_account_id,
            transaction_amount=required_amount,
            currency="USD",
            transaction_status="pending",
            description=payment_data.description
        )
        
        db.add(payment)
        await db.flush()  # Get payment created_at timestamp
        
        # Step 7: Create initial log entry (null -> pending)
        log = PaymentLog(
            transaction_id=transaction_id,
            old_status=None,
            new_status="pending"
        )
        
        db.add(log)
        await db.commit()
        await db.refresh(payment)
        
        return payment
    
    @staticmethod
    async def get_payment_by_id(
        db: AsyncSession,
        transaction_id: str,
        include_logs: bool = False
    ) -> Optional[Payment]:
        """
        Get payment by transaction ID
        
        Args:
            db: Database session
            transaction_id: Transaction identifier
            include_logs: Whether to eagerly load logs
            
        Returns:
            Payment if found, None otherwise
        """
        query = select(Payment).where(Payment.transaction_id == transaction_id)
        
        # Always load account relationships (needed for response serialization)
        query = query.options(
            selectinload(Payment.debtor_account),
            selectinload(Payment.creditor_account)
        )
        
        # Optionally load logs
        if include_logs:
            query = query.options(selectinload(Payment.logs))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_payments(
        db: AsyncSession,
        page: int = 1,
        limit: int = 10,
        status: Optional[str] = None
    ) -> tuple[List[Payment], int]:
        """
        Get paginated list of payments
        
        Args:
            db: Database session
            page: Page number (1-indexed)
            limit: Items per page
            status: Filter by status (optional)
            
        Returns:
            Tuple of (payments_list, total_count)
        """
        # Base query
        query = select(Payment).options(
            selectinload(Payment.debtor_account),
            selectinload(Payment.creditor_account)
        )
        
        # Apply status filter if provided
        if status:
            query = query.where(Payment.transaction_status == status)
        
        # Order by created_at descending (newest first)
        query = query.order_by(desc(Payment.created_at))
        
        # Get total count
        count_query = select(func.count()).select_from(Payment)
        if status:
            count_query = count_query.where(Payment.transaction_status == status)
        
        total_result = await db.execute(count_query)
        total_count = total_result.scalar()
        
        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        payments = list(result.scalars().all())
        
        return payments, total_count
    
    @staticmethod
    async def update_payment_status(
        db: AsyncSession,
        transaction_id: str,
        new_status: str,
        error_message: Optional[str] = None
    ) -> Payment:
        """
        Update payment status and create log entry
        
        Args:
            db: Database session
            transaction_id: Transaction to update
            new_status: New status value
            error_message: Error message (for failed status)
            
        Returns:
            Updated payment
            
        Raises:
            PaymentNotFoundException: If payment doesn't exist
        """
        # Get payment
        payment = await db.get(Payment, transaction_id)
        if not payment:
            raise PaymentNotFoundException(transaction_id)
        
        # Store old status
        old_status = payment.transaction_status
        
        # Update payment status
        payment.transaction_status = new_status
        payment.error_message = error_message
        
        # Set completed_at if reaching final status
        if new_status in ("completed", "failed"):
            payment.completed_at = datetime.utcnow()
        
        # Create log entry
        log = PaymentLog(
            transaction_id=transaction_id,
            old_status=old_status,
            new_status=new_status,
            error_message=error_message
        )
        
        db.add(log)
        await db.commit()
        await db.refresh(payment)
        
        return payment
    
    @staticmethod
    async def complete_payment(
        db: AsyncSession,
        transaction_id: str
    ) -> Payment:
        """
        Complete a payment: transfer funds and update status
        
        This is a transactional operation:
        1. Deduct from debtor account
        2. Add to creditor account
        3. Update payment status to 'completed'
        4. Create log entry
        
        Args:
            db: Database session
            transaction_id: Transaction to complete
            
        Returns:
            Completed payment
            
        Raises:
            PaymentNotFoundException: If payment doesn't exist
            InsufficientBalanceException: If balance check fails
        """
        async with db.begin_nested():  # Savepoint for sub-transaction
            # Get payment with account relationships
            result = await db.execute(
                select(Payment)
                .where(Payment.transaction_id == transaction_id)
                .options(
                    selectinload(Payment.debtor_account),
                    selectinload(Payment.creditor_account)
                )
            )
            payment = result.scalar_one_or_none()
            
            if not payment:
                raise PaymentNotFoundException(transaction_id)
            
            # Re-check balance (in case it changed)
            if payment.debtor_account.balance < payment.transaction_amount:
                raise InsufficientBalanceException(
                    account_id=payment.debtor_account_id,
                    available=payment.debtor_account.balance,
                    required=payment.transaction_amount
                )
            
            # Transfer funds
            payment.debtor_account.balance -= payment.transaction_amount
            payment.creditor_account.balance += payment.transaction_amount
            
            # Update payment status
            old_status = payment.transaction_status
            payment.transaction_status = "completed"
            payment.completed_at = datetime.utcnow()
            
            # Create log entry
            log = PaymentLog(
                transaction_id=transaction_id,
                old_status=old_status,
                new_status="completed"
            )
            db.add(log)
        
        await db.commit()
        await db.refresh(payment)
        return payment
    
    @staticmethod
    async def fail_payment(
        db: AsyncSession,
        transaction_id: str,
        error_message: str
    ) -> Payment:
        """
        Mark payment as failed
        
        Args:
            db: Database session
            transaction_id: Transaction to fail
            error_message: Reason for failure
            
        Returns:
            Failed payment
        """
        payment = await db.get(Payment, transaction_id)
        if not payment:
            raise PaymentNotFoundException(transaction_id)
        
        old_status = payment.transaction_status
        payment.transaction_status = "failed"
        payment.error_message = error_message
        payment.completed_at = datetime.utcnow()
        
        # Create log entry
        log = PaymentLog(
            transaction_id=transaction_id,
            old_status=old_status,
            new_status="failed",
            error_message=error_message
        )
        
        db.add(log)
        await db.commit()
        await db.refresh(payment)
        
        return payment
