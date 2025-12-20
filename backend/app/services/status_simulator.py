"""
Payment Status Simulator

Simulates payment processing by transitioning statuses asynchronously.
"""

import asyncio
import random
from typing import Optional

from app.core.database import AsyncSessionLocal
from app.services.payment_service import PaymentService
from app.core.config import settings


class PaymentStatusSimulator:
    """
    Simulates payment gateway processing
    
    Status flow:
        pending (0s)
          ↓ (2s delay)
        processing
          ↓ (3-6s random delay)
        completed (90% chance) OR failed (10% chance)
    
    Why simulate?
    - Real payment gateways are asynchronous
    - Demonstrates status tracking
    - Tests frontend polling mechanism
    """
    
    # Error messages for failed payments (random selection)
    FAILURE_MESSAGES = [
        "Insufficient funds at payment gateway",
        "Creditor account temporarily unavailable",
        "Transaction timeout - please retry",
        "Anti-fraud system flagged this transaction",
        "Network error during processing"
    ]
    
    @classmethod
    async def simulate_payment_processing(
        cls,
        transaction_id: str
    ) -> None:
        """
        Simulate payment processing asynchronously
        
        This runs as a background task after payment creation.
        
        Args:
            transaction_id: Payment to process
        """
        async with AsyncSessionLocal() as db:
            try:
                # ========================================
                # Phase 1: pending → processing
                # ========================================
                await asyncio.sleep(
                    settings.PAYMENT_PENDING_TO_PROCESSING_DELAY
                )
                
                await PaymentService.update_payment_status(
                    db=db,
                    transaction_id=transaction_id,
                    new_status="processing"
                )
                
                # ========================================
                # Phase 2: processing → completed/failed
                # ========================================
                processing_delay = random.uniform(
                    settings.PAYMENT_PROCESSING_MIN_DELAY,
                    settings.PAYMENT_PROCESSING_MAX_DELAY
                )
                await asyncio.sleep(processing_delay)
                
                # Determine success/failure (based on configured success rate)
                success = random.random() < settings.PAYMENT_SUCCESS_RATE
                
                if success:
                    # Complete payment (transfer funds)
                    await PaymentService.complete_payment(
                        db=db,
                        transaction_id=transaction_id
                    )
                else:
                    # Fail payment (random error message)
                    error_message = random.choice(cls.FAILURE_MESSAGES)
                    await PaymentService.fail_payment(
                        db=db,
                        transaction_id=transaction_id,
                        error_message=error_message
                    )
                
            except Exception as e:
                # If any error occurs, mark payment as failed
                try:
                    await PaymentService.fail_payment(
                        db=db,
                        transaction_id=transaction_id,
                        error_message=f"System error: {str(e)}"
                    )
                except:
                    # Log error (in production, use proper logging)
                    print(f"Critical error processing payment {transaction_id}: {e}")
    
    @classmethod
    def start_simulation(cls, transaction_id: str) -> asyncio.Task:
        """
        Start payment simulation as a background task
        
        Args:
            transaction_id: Payment to simulate
            
        Returns:
            Asyncio task (can be used to track/cancel)
        """
        return asyncio.create_task(
            cls.simulate_payment_processing(transaction_id)
        )
