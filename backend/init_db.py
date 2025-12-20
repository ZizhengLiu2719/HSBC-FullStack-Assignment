import asyncio
import sys
from app.core.database import init_db, drop_db, engine


async def main():
    """Main initialization function"""
    print("=" * 60)
    print("Database Initialization")
    print("=" * 60)
    
    # Check if --reset flag is provided
    if "--reset" in sys.argv:
        print("\n⚠️  WARNING: Dropping all existing tables...")
        confirm = input("Are you sure? (yes/no): ")
        if confirm.lower() == "yes":
            await drop_db()
        else:
            print("Aborted.")
            return
    
    # Create tables
    print("\nCreating database tables...")
    await init_db()
    
    # Load seed data if --seed flag is provided
    if "--seed" in sys.argv:
        print("\nLoading seed data...")
        from data.seed_data import load_seed_data
        await load_seed_data()
    
    print("\n" + "=" * 60)
    print("✅ Database initialization complete!")
    print("=" * 60)
    
    # Close engine
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())