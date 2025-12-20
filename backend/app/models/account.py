"""
Account Model

Represents a bank account (debtor or creditor)
"""

from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Numeric, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.payment import Payment


class Account(Base):
   
    __tablename__ = "accounts"
    
    
    # Primary Key
    account_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        comment="Unique account identifier"
    )
    
    # Account Information
    account_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Display name of the account"
    )
    
    account_type: Mapped[str] = mapped_column(
        Enum("debtor", "creditor", name="account_type_enum"),
        nullable=False,
        index=True,  # Index for filtering by type
        comment="Type: 'debtor' (pays) or 'creditor' (receives)"
    )
    
    # Financial Information
    balance: Mapped[float] = mapped_column(
        Numeric(precision=18, scale=2),  # Up to 16 digits before decimal, 2 after
        nullable=False,
        default=0.00,
        comment="Current balance in USD"
    )
    
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="USD",
        comment="Currency code (ISO 4217)"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),  # Database sets this automatically
        nullable=False,
        comment="When account was created"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),  # Auto-update on any change
        nullable=False,
        comment="When account was last updated"
    )
    
    # One account can have many payments as debtor
    debtor_payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="debtor_account",
        foreign_keys="Payment.debtor_account_id",
        cascade="all, delete-orphan"  # Delete payments if account deleted
    )
    
    # One account can have many payments as creditor
    creditor_payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="creditor_account",
        foreign_keys="Payment.creditor_account_id",
        cascade="all, delete-orphan"
    )
    
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return (
            f"<Account(id={self.account_id}, "
            f"name={self.account_name}, "
            f"type={self.account_type}, "
            f"balance={self.balance})>"
        )