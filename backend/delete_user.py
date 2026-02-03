"""
Delete User from Database
Safely remove a user by email address
"""
import asyncio
from sqlalchemy import select, delete
from app.database import AsyncSessionLocal
from app.models.user import User


async def delete_user_by_email(email: str):
    """Delete user by email address"""
    async with AsyncSessionLocal() as db:
        # First, check if user exists
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ User with email '{email}' not found in database")
            return False
        
        # Show user details before deletion
        print("\n" + "="*60)
        print("Found user to delete:")
        print("="*60)
        print(f"  Email: {user.email}")
        print(f"  Name: {user.full_name}")
        print(f"  Organization: {user.organization}")
        print(f"  Created: {user.created_at}")
        print(f"  Email Verified: {user.email_verified}")
        print("="*60)
        
        # Confirm deletion
        confirm = input("\n⚠️  Are you sure you want to delete this user? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("❌ Deletion cancelled")
            return False
        
        # Delete user
        await db.execute(delete(User).where(User.email == email))
        await db.commit()
        
        print(f"\n✅ User '{email}' deleted successfully")
        return True


if __name__ == "__main__":
    import sys
    
    # Get email from command line or use default
    if len(sys.argv) > 1:
        email_to_delete = sys.argv[1]
    else:
        email_to_delete = "info@teachgenie.ai"
    
    print(f"\n🗑️  Deleting user: {email_to_delete}")
    asyncio.run(delete_user_by_email(email_to_delete))
