"""
Seed Data Script

Populates database with initial test data.

Usage:
    python seed_data.py
"""

import asyncio
from app.core.database import AsyncSessionLocal, init_db, drop_db
from app.models.account import Account


async def seed_accounts():
    """Create demo accounts with initial balances"""
    
    accounts_data = [
        # Debtor accounts (company accounts that make payments)
        {
            "account_id": "ACC001",
            "account_name": "Main Operating Account",
            "account_type": "debtor",
            "balance": 100000.00,
            "currency": "USD"
        },
        {
            "account_id": "ACC002",
            "account_name": "Payroll Account",
            "account_type": "debtor",
            "balance": 50000.00,
            "currency": "USD"
        },
        {
            "account_id": "ACC003",
            "account_name": "Marketing Budget",
            "account_type": "debtor",
            "balance": 25000.00,
            "currency": "USD"
        },
        
        # Creditor accounts (suppliers/vendors that receive payments)
        {
            "account_id": "SUP001",
            "account_name": "Office Supplies Inc.",
            "account_type": "creditor",
            "balance": 0.00,
            "currency": "USD"
        },
        {
            "account_id": "SUP002",
            "account_name": "Tech Solutions Ltd.",
            "account_type": "creditor",
            "balance": 0.00,
            "currency": "USD"
        },
        {
            "account_id": "SUP003",
            "account_name": "Consulting Partners",
            "account_type": "creditor",
            "balance": 0.00,
            "currency": "USD"
        },
        {
            "account_id": "SUP004",
            "account_name": "Cloud Services Provider",
            "account_type": "creditor",
            "balance": 0.00,
            "currency": "USD"
        },
    ]
    
    async with AsyncSessionLocal() as db:
        # Create accounts
        for account_data in accounts_data:
            account = Account(**account_data)
            db.add(account)
        
        await db.commit()
        print(f"[OK] Created {len(accounts_data)} accounts")


async def main():
    """Main seed function"""
    
    print("="*60)
    print("Seeding Database")
    print("="*60)
    
    # Drop and recreate tables (fresh start)
    await drop_db()
    await init_db()
    
    # Seed accounts
    await seed_accounts()
    
    print("="*60)
    print("[SUCCESS] Database seeded successfully!")
    print()
    print("Available accounts:")
    print()
    print("Debtor Accounts (for making payments):")
    print("  - ACC001: Main Operating Account ($100,000)")
    print("  - ACC002: Payroll Account ($50,000)")
    print("  - ACC003: Marketing Budget ($25,000)")
    print()
    print("Creditor Accounts (for receiving payments):")
    print("  - SUP001: Office Supplies Inc.")
    print("  - SUP002: Tech Solutions Ltd.")
    print("  - SUP003: Consulting Partners")
    print("  - SUP004: Cloud Services Provider")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
