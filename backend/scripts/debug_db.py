import asyncio
import sys
import os
import asyncpg
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import settings

async def test_connection():
    print("Trying raw asyncpg connection...")
    
    # Extract DSN from SQLAlchemy URL (remove 'postgresql+asyncpg://')
    dsn = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    try:
        conn = await asyncpg.connect(dsn, statement_cache_size=0)
        version = await conn.fetchval("SELECT version()")
        print(f"✅ Success! Version: {version}")
        await conn.close()
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
