"""
Quick test script to debug registration endpoint
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import UserCreate
from app.models.user import User
from sqlalchemy import select
from app.core.security import hash_password

async def test_registration():
    """Test user registration with debug output"""
    
    # Create test user data
    user_data = UserCreate(
        email="testdebug@example.com",
        password="Test1234",
        full_name="Test User",
        organization="Test Org",
        country="India",
        phone_number="+1234567890"
    )
    
    print(f"✅ User data created: {user_data}")
    print(f"📋 User data dict: {user_data.dict()}")
    
    # Get database session
    async for db in get_db():
        try:
            # Check if email exists
            result = await db.execute(select(User).where(User.email == user_data.email))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"⚠️ User already exists, deleting...")
                await db.delete(existing_user)
                await db.commit()
            
            # Create new user
            print("📝 Creating new user...")
            new_user = User(
                email=user_data.email,
                password_hash=hash_password(user_data.password),
                full_name=user_data.full_name,
                organization=user_data.organization,
                country=getattr(user_data, 'country', None),
                phone_number=getattr(user_data, 'phone_number', None),
                is_active=True,
                is_verified=False
            )
            
            print(f"✅ User object created: {new_user}")
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            print(f"✅ ✅ SUCCESS! User registered: {new_user.email}, ID: {new_user.id}")
            
        except Exception as e:
            print(f"❌ ERROR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()
        
        break  # Exit after first session

if __name__ == "__main__":
    asyncio.run(test_registration())
