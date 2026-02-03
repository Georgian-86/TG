"""
Minimal test to run registration without FastAPI wrapper - NO UNICODE
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
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
            email="simple_test@example.com",
            password="Test1234",
            full_name="Simple Test",
            organization="Test Org"
        )
        
        print("OK: User data validated")
        print(f"Email: {user_data.email}")
        
        async with SessionLocal() as db:
            # Create new user
            new_user = User(
                email=user_data.email,
                password_hash=hash_password(user_data.password),
                full_name=user_data.full_name,
                organization=user_data.organization,
                country= None,
                phone_number=None,
                is_active=True,
                is_verified=False
            )
            
            print("OK: User object created")
            
            db.add(new_user)
            print("OK: User added to session")
            
            await db.commit()
            print("OK: Database commit successful")
            
            await db.refresh(new_user)
            print("OK: User refreshed from database")
            
            print(f"SUCCESS! User created - Email: {new_user.email}, ID: {new_user.id}")
            print(f"Full name: {new_user.full_name}, Organization: {new_user.organization}")
            return True
            
    except Exception as e:
        print(f"ERROR: {type(e).__name__}")
        print(f"Message: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_direct_registration())
    print(f"\nFinal result: {'SUCCESS' if result else 'FAILED'}")
