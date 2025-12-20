"""
Account Service

Handles account-related business logic.
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account


class AccountService:
    """
    Service for account operations
    
    Why a service layer?
    - Separates business logic from API endpoints
    - Makes code reusable
    - Easier to test
    - Can be used by multiple endpoints
    """
    
    @staticmethod
    async def get_all_accounts(db: AsyncSession) -> List[Account]:
        """
        Retrieve all accounts from database
        
        Args:
            db: Database session
            
        Returns:
            List of all accounts
        """
        result = await db.execute(select(Account))
        return list(result.scalars().all())
    
    @staticmethod
    async def get_account_by_id(
        db: AsyncSession, 
        account_id: str
    ) -> Optional[Account]:
        """
        Get a single account by ID
        
        Args:
            db: Database session
            account_id: Account identifier
            
        Returns:
            Account if found, None otherwise
        """
        return await db.get(Account, account_id)
    
    @staticmethod
    async def get_accounts_by_type(
        db: AsyncSession,
        account_type: str
    ) -> List[Account]:
        """
        Get all accounts of a specific type
        
        Args:
            db: Database session
            account_type: 'debtor' or 'creditor'
            
        Returns:
            List of accounts matching the type
        """
        result = await db.execute(
            select(Account).where(Account.account_type == account_type)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def check_sufficient_balance(
        db: AsyncSession,
        account_id: str,
        required_amount: float
    ) -> bool:
        """
        Check if account has sufficient balance
        
        Args:
            db: Database session
            account_id: Account to check
            required_amount: Required amount
            
        Returns:
            True if balance is sufficient, False otherwise
        """
        account = await db.get(Account, account_id)
        if not account:
            return False
        return account.balance >= required_amount
    
    @staticmethod
    async def update_balance(
        db: AsyncSession,
        account_id: str,
        amount: float,
        operation: str = "add"
    ) -> Optional[Account]:
        """
        Update account balance
        
        Args:
            db: Database session
            account_id: Account to update
            amount: Amount to add/subtract
            operation: 'add' or 'subtract'
            
        Returns:
            Updated account or None if not found
        """
        account = await db.get(Account, account_id)
        if not account:
            return None
        
        if operation == "add":
            account.balance += amount
        elif operation == "subtract":
            account.balance -= amount
        else:
            raise ValueError(f"Invalid operation: {operation}")
        
        await db.commit()
        await db.refresh(account)
        return account
