"""
Minimal test to run registration without FastAPI wrapper
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password

# Create async engine
DATABASE_URL = "sqlite+aiosqlite:///./teachgenie.db"
engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def test_direct_registration():
    """Test registration directly"""
    try:
        user_data = UserCreate(
            email="direct_test@example.com",
            password="Test1234",
            full_name="Direct Test",
            organization="Test Org"
        )
        
        print(f"✅ User data validated: {user_data}")
        
        async with SessionLocal() as db:
            # Create new user
            new_user = User(
                email=user_data.email,
                password_hash=hash_password(user_data.password),
                full_name=user_data.full_name,
                organization=user_data.organization,
                country=None,
                phone_number=None,
                is_active=True,
                is_verified=False
            )
            
            print(f"✅ User object created")
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            print(f"✅✅ SUCCESS! User created: {new_user.email}, ID: {new_user.id}")
            print(f"User details: full_name={new_user.full_name}, org={new_user.organization}")
            
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct_registration())
