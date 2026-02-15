"""
Set Unlimited Access for Specific Users
========================================
Upgrades specified user emails to PRO tier (unlimited lesson generation).

Usage:
    python backend/set_unlimited_users.py
"""
import asyncio
import os
import sys

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==============================
# ADD UNLIMITED USER EMAILS HERE
# ==============================
UNLIMITED_USERS = [
    "optimus4586prime@gmail.com",
    "medhajha810@gmail.com",
    "info@teachgenie.ai",
]


async def set_unlimited():
    # Use DATABASE_URL env var if set, otherwise default to local SQLite
    db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./teachgenie.db")
    
    # Handle Railway/Heroku postgres:// -> postgresql+asyncpg://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("postgresql://") and "asyncpg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    display_url = db_url.split("@")[-1] if "@" in db_url else db_url
    print(f"Connecting to: {display_url}")
    
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import text

    connect_args = {"check_same_thread": False} if "sqlite" in db_url else {}
    engine = create_async_engine(db_url, connect_args=connect_args)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        for email in UNLIMITED_USERS:
            # Check if user exists first
            result = await session.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": email}
            )
            user = result.scalar()
            
            if user:
                # Update to PRO
                await session.execute(
                    text("""
                        UPDATE users 
                        SET subscription_tier = 'pro', lessons_this_month = 0
                        WHERE email = :email
                    """),
                    {"email": email}
                )
                print(f"✅ {email} → PRO (unlimited access, counter reset)")
            else:
                print(f"⚠️  {email} → NOT FOUND in database")
        
        await session.commit()
    
    await engine.dispose()
    print("\nDone! PRO users have unlimited lesson generation (999,999/month).")


if __name__ == "__main__":
    print("=" * 50)
    print("TeachGenie - Set Unlimited Access")
    print("=" * 50)
    asyncio.run(set_unlimited())
