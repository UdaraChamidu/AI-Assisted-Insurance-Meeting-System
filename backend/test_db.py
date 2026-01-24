"""
Quick test to check if database connection works
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_db():
    try:
        # Use the same DATABASE_URL from .env
        DATABASE_URL = "postgresql+asyncpg://postgres:udara@localhost:5432/insurance_agent"
        
        engine = create_async_engine(DATABASE_URL)
        
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Database connection successful!")
            print(f"PostgreSQL version: {version}")
            
            # Check if database exists
            result = await conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f"Current database: {db_name}")
            
            # List tables
            result = await conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = result.fetchall()
            print(f"\nTables in database:")
            if tables:
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("  (no tables found)")
        
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Database connection failed!")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_db())
