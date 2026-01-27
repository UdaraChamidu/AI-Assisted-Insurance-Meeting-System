"""
Script to create initial admin user for the insurance agent system.
Uses raw asyncpg to avoid SQLAlchemy pooling conflicts.
"""
import asyncio
import sys
from pathlib import Path
import asyncpg
import bcrypt  # Uses direct bcrypt instead of passlib

# Add parent directory to path to import from backend
sys.path.insert(0, str(Path(__file__).parent))

from config import settings

def hash_password(password: str) -> str:
    """Hash a password using bcrypt directly."""
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')

async def create_user_raw(conn, email, password, full_name, role):
    # Check valid enum values
    try:
        enums = await conn.fetch("""
            SELECT e.enumlabel
            FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'userrole'
        """)
        valid_roles = [r['enumlabel'] for r in enums]
        print(f"ℹ️ Valid 'userrole' values in DB: {valid_roles}")
        
        # Adjust role to match case if found
        for r_val in valid_roles:
            if r_val.lower() == role.lower():
                print(f"🔄 Adjusting role '{role}' to '{r_val}'")
                role = r_val
                break
    except Exception as e:
        print(f"⚠️ Could not check enums: {e}")

    # Check if exists
    exists = await conn.fetchval("SELECT id FROM users WHERE email = $1", email)
    if exists:
        print(f"❌ User '{email}' already exists.")
        return

    hashed = hash_password(password)
    await conn.execute("""
        INSERT INTO users (id, email, hashed_password, full_name, role, is_active, created_at, updated_at)
        VALUES (gen_random_uuid(), $1, $2, $3, $4, true, now(), now())
    """, email, hashed, full_name, role)
    
    print(f"✅ User '{email}' created successfully ({role}).")

async def main():
    print("🚀 Creating users with raw asyncpg...")
    dsn = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    try:
        conn = await asyncpg.connect(dsn, statement_cache_size=0)
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    users = [
        ("admin@insurance.com", "admin123", "Admin User", "admin"),
        ("agent@insurance.com", "agent123", "Agent Smith", "agent")
    ]

    try:
        for email, pwd, name, role in users:
            await create_user_raw(conn, email, pwd, name, role)
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())


