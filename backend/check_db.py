"""Temporary script: Check database contents"""
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "payment_system.db"

if not db_path.exists():
    print(f"[ERROR] Database file not found: {db_path}")
    exit(1)

print(f"[OK] Database file exists: {db_path}")
print(f"[INFO] File size: {db_path.stat().st_size / 1024:.2f} KB")
print()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check tables
print("=== DATABASE TABLES ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table[0]}")
print()

# Check accounts
cursor.execute("SELECT COUNT(*) FROM accounts")
count = cursor.fetchone()[0]
print(f"Total Accounts: {count}")
print()

if count > 0:
    print("=== ACCOUNT LIST ===")
    cursor.execute("""
        SELECT account_id, account_name, account_type, balance 
        FROM accounts 
        ORDER BY account_type, account_id
    """)
    accounts = cursor.fetchall()
    
    print("\n  Debtor Accounts (Payers):")
    for acc in accounts:
        if acc[2] == 'debtor':
            print(f"    {acc[0]}: {acc[1]} - ${acc[3]:,.2f}")
    
    print("\n  Creditor Accounts (Payees):")
    for acc in accounts:
        if acc[2] == 'creditor':
            print(f"    {acc[0]}: {acc[1]} - ${acc[3]:,.2f}")

# Check payments
cursor.execute("SELECT COUNT(*) FROM payments")
payment_count = cursor.fetchone()[0]
print(f"\nTotal Payments: {payment_count}")

if payment_count > 0:
    cursor.execute("""
        SELECT transaction_id, transaction_status, transaction_amount, created_at
        FROM payments
        ORDER BY created_at DESC
        LIMIT 5
    """)
    payments = cursor.fetchall()
    print("\nRecent Payments:")
    for p in payments:
        print(f"  {p[0]} - {p[1]} - ${p[2]:,.2f} - {p[3]}")

conn.close()
print("\n[OK] Database check complete!")
