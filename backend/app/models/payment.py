"""
Payment Model

Represents a payment transaction between two accounts
"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    String, Numeric, Enum, DateTime, Text, ForeignKey,
    CheckConstraint, Index, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.payment_log import PaymentLog


class Payment(Base):
    """
    Payment transaction table
    
    Represents a payment from debtor account to creditor account.
    Tracks status changes through PaymentLog entries.
    
    Status flow:
        pending → processing → completed/failed
    """
    
    __tablename__ = "payments"
    
    
    # Primary Key
    transaction_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        comment="Unique transaction identifier (e.g., TXN_20250118_xxxxx)"
    )
    
    # Account References (Foreign Keys)
    debtor_account_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("accounts.account_id", ondelete="CASCADE"),
        nullable=False,
        index=True,  # Index for queries filtering by debtor
        comment="Account ID of the payer"
    )
    
    creditor_account_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("accounts.account_id", ondelete="CASCADE"),
        nullable=False,
        index=True,  # Index for queries filtering by creditor
        comment="Account ID of the payee"
    )
    
    # Transaction Details
    transaction_amount: Mapped[float] = mapped_column(
        Numeric(precision=18, scale=2),
        nullable=False,
        comment="Amount to transfer in USD"
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
        comment="Currency code (ISO 4217)"
    )
    
    # Status
    transaction_status: Mapped[str] = mapped_column(
        Enum("pending", "processing", "completed", "failed", 
             name="payment_status_enum"),
        nullable=False,
        default="pending",
        index=True,  # Index for filtering by status
        comment="Current status of the payment"
    )
    
    # Optional Fields
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Payment description/notes"
    )
    
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error details if status is 'failed'"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,  # Index for sorting by creation time
        comment="When payment was created"
    )
    
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
        comment="When payment was last updated"
    )
    
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When payment reached final status (completed/failed)"
    )
    
    
    # Many payments belong to one debtor account
    debtor_account: Mapped["Account"] = relationship(
        "Account",
        back_populates="debtor_payments",
        foreign_keys=[debtor_account_id]
    )
    
    # Many payments belong to one creditor account
    creditor_account: Mapped["Account"] = relationship(
        "Account",
        back_populates="creditor_payments",
        foreign_keys=[creditor_account_id]
    )
    
    # One payment has many log entries
    logs: Mapped[list["PaymentLog"]] = relationship(
        "PaymentLog",
        back_populates="payment",
        cascade="all, delete-orphan",
        order_by="PaymentLog.created_at"  # Order logs chronologically
    )
    
    
    __table_args__ = (
        # Ensure amount is positive
        CheckConstraint(
            "transaction_amount > 0",
            name="check_positive_amount"
        ),
        
        # Ensure debtor and creditor are different
        CheckConstraint(
            "debtor_account_id != creditor_account_id",
            name="check_different_accounts"
        ),
        
        # Composite index for common queries
        Index(
            "idx_payment_status_created",
            "transaction_status",
            "created_at"
        ),
    )

    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return (
            f"<Payment(id={self.transaction_id}, "
            f"amount={self.transaction_amount}, "
            f"status={self.transaction_status})>"
        )