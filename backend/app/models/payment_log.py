from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import String, Enum, DateTime, Text, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.payment import Payment


class PaymentLog(Base):
    """
    Payment log table for audit trail
    
    Records every status change of a payment transaction.
    Provides complete history for debugging and compliance.
    
    Example log sequence:
        1. old_status=NULL,      new_status=pending
        2. old_status=pending,   new_status=processing
        3. old_status=processing, new_status=completed
    """
    
    __tablename__ = "payment_logs"
    
    
    # Primary Key (auto-increment)
    log_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        comment="Unique log entry ID"
    )
    
    # Foreign Key to Payment
    transaction_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("payments.transaction_id", ondelete="CASCADE"),
        nullable=False,
        index=True,  # Index for querying logs by transaction
        comment="Reference to payment transaction"
    )
    
    # Status Change
    old_status: Mapped[Optional[str]] = mapped_column(
        Enum("pending", "processing", "completed", "failed",
             name="payment_status_enum"),
        nullable=True,  # NULL for initial log entry
        comment="Previous status (NULL for first log)"
    )
    
    new_status: Mapped[str] = mapped_column(
        Enum("pending", "processing", "completed", "failed",
             name="payment_status_enum"),
        nullable=False,
        comment="New status after change"
    )
    
    # Optional Error Information
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error details if transitioning to 'failed'"
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When this status change occurred"
    )
    
    
    # Many logs belong to one payment
    payment: Mapped["Payment"] = relationship(
        "Payment",
        back_populates="logs"
    )
    
    
    __table_args__ = (
        # Composite index for fetching logs by transaction (ordered)
        Index(
            "idx_log_transaction_created",
            "transaction_id",
            "created_at"
        ),
    )
    
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return (
            f"<PaymentLog(id={self.log_id}, "
            f"transaction={self.transaction_id}, "
            f"{self.old_status}→{self.new_status})>"
        )