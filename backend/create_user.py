"""
Script to create initial admin user for the insurance agent system.
Run this after setting up the database to create your first admin account.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import from backend
sys.path.insert(0, str(Path(__file__).parent))

from database import init_db, AsyncSessionLocal
from db_models import User
from auth.password import hash_password
from sqlalchemy import select


async def create_admin_user(
    email: str,
    password: str,
    full_name: str,
    role: str = "admin"
):
    """Create an admin user in the database."""
    
    # Initialize database
    await init_db()
    
    async with AsyncSessionLocal() as session:
        # Check if user already exists
        result = await session.execute(
            select(User).where(User.email == email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"❌ User with email '{email}' already exists!")
            return False
        
        # Create new admin user
        hashed_password = hash_password(password)
        new_user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            is_active=True
        )
        
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        
        print(f"\n✅ Admin user created successfully!")
        print(f"   Email: {email}")
        print(f"   Name: {full_name}")
        print(f"   Role: {role}")
        print(f"   User ID: {new_user.id}")
        print("\n🔐 You can now login with these credentials.\n")
        
        return True


async def create_test_users():
    """Create a set of test users for development."""
    
    users = [
        {
            "email": "admin@insurance.com",
            "password": "admin123",
            "full_name": "Admin User",
            "role": "admin"
        },
        {
            "email": "agent@insurance.com",
            "password": "agent123",
            "full_name": "Agent Smith",
            "role": "agent"
        }
    ]
    
    print("\n🚀 Creating test users...\n")
    
    for user_data in users:
        await create_admin_user(**user_data)


async def interactive_create():
    """Interactive user creation."""
    print("\n" + "="*60)
    print("  CREATE ADMIN USER")
    print("="*60 + "\n")
    
    email = input("Enter email: ").strip()
    password = input("Enter password: ").strip()
    full_name = input("Enter full name: ").strip()
    role = input("Enter role (admin/agent) [admin]: ").strip() or "admin"
    
    if role not in ["admin", "agent"]:
        print("❌ Invalid role! Use 'admin' or 'agent'")
        return
    
    await create_admin_user(email, password, full_name, role)


async def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            # Create test users
            await create_test_users()
        elif sys.argv[1] == "--help":
            print("\nUsage:")
            print("  python create_user.py              # Interactive mode")
            print("  python create_user.py --test       # Create test users")
            print("  python create_user.py --help       # Show this help")
            print("\nTest Users:")
            print("  admin@insurance.com / admin123 (admin)")
            print("  agent@insurance.com / agent123 (agent)")
            print()
        else:
            print(f"❌ Unknown option: {sys.argv[1]}")
            print("   Use --help for usage information")
    else:
        # Interactive mode
        await interactive_create()


if __name__ == "__main__":
    asyncio.run(main())
