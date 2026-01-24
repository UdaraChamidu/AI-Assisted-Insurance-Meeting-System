"""
Drop and recreate all database tables.
WARNING: This will delete all data!
"""
import asyncio
from sqlalchemy import text
from database import engine, Base, init_db
from db_models import *  # Import all models

async def reset_database():
    print("⚠️  WARNING: This will DROP ALL TABLES and DATA!")
    response = input("Type 'yes' to continue: ")
    
    if response.lower() != 'yes':
        print("❌ Aborted")
        return
    
    print("\n🗑️  Dropping all tables...")
    async with engine.begin() as conn:
        # Use CASCADE to drop tables with dependencies
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.commit()
    print("✅ All tables dropped")
    
    print("\n📋 Creating all tables...")
    await init_db()
    print("✅ All tables created")
    
    print("\n✅ Database reset complete!")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(reset_database())
